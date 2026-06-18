"""AI Administrator — natural language network & system analysis using LLM"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User
from app.models.computer import Computer
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/ai", tags=["AI Administrator"])


def _format_bits(bps: float) -> str:
    if bps >= 1_000_000_000:
        return f"{bps/1_000_000_000:.1f} Gbps"
    if bps >= 1_000_000:
        return f"{bps/1_000_000:.1f} Mbps"
    if bps >= 1_000:
        return f"{bps/1_000:.1f} Kbps"
    return f"{bps:.0f} bps"


def _format_bytes(b: int) -> str:
    if b >= 1_073_741_824:
        return f"{b/1_073_741_824:.1f} GB"
    if b >= 1_048_576:
        return f"{b/1_048_576:.1f} MB"
    if b >= 1_024:
        return f"{b/1_024:.1f} KB"
    return f"{b} B"


async def _gather_network_context(db: AsyncSession, org_id: str | None) -> dict:
    """Collect all network data for AI analysis."""
    ctx = {}

    from app.models.network_device import NetworkDevice, BandwidthRecord, PingResult
    from app.models.traffic_log import TrafficLog
    from app.models.firewall_rule import FirewallRule
    from app.models.internet_rule import InternetRule

    f = {"organization_id": org_id} if org_id else {}

    # Device count by type
    dev_q = select(NetworkDevice.device_type, func.count()).group_by(NetworkDevice.device_type)
    if org_id:
        dev_q = dev_q.where(NetworkDevice.organization_id == org_id)
    rows = (await db.execute(dev_q)).all()
    ctx["devices"] = {r[0].value if hasattr(r[0], 'value') else r[0]: r[1] for r in rows}

    # Total devices monitored
    ctx["total_devices"] = sum(ctx["devices"].values()) if ctx["devices"] else 0

    # Bandwidth top devices
    bw_q = select(
        BandwidthRecord.device_id,
        func.avg(BandwidthRecord.utilization_pct).label("avg_util"),
        func.avg(BandwidthRecord.bits_in_per_sec).label("avg_in"),
        func.avg(BandwidthRecord.bits_out_per_sec).label("avg_out"),
    )
    if org_id:
        bw_q = bw_q.where(BandwidthRecord.organization_id == org_id)
    bw_q = bw_q.group_by(BandwidthRecord.device_id).order_by(desc("avg_util")).limit(5)
    bw_rows = (await db.execute(bw_q)).all()
    ctx["top_bandwidth_devices"] = []
    for r in bw_rows:
        dev = await db.get(NetworkDevice, r.device_id)
        ctx["top_bandwidth_devices"].append({
            "hostname": dev.hostname if dev else "Unknown",
            "avg_util_pct": round(r.avg_util or 0, 1),
            "avg_in": _format_bits(r.avg_in or 0),
            "avg_out": _format_bits(r.avg_out or 0),
        })

    # Ping status
    subq = select(
        PingResult.device_id,
        func.max(PingResult.checked_at).label("latest")
    )
    if org_id:
        subq = subq.where(PingResult.organization_id == org_id)
    subq = subq.group_by(PingResult.device_id).subquery()
    ping_q = select(PingResult, NetworkDevice.hostname).join(
        subq, (PingResult.device_id == subq.c.device_id) & (PingResult.checked_at == subq.c.latest)
    ).join(NetworkDevice, NetworkDevice.id == PingResult.device_id)
    ping_rows = (await db.execute(ping_q)).all()
    alive = sum(1 for r in ping_rows if r[0].is_alive)
    dead = sum(1 for r in ping_rows if not r[0].is_alive)
    high_latency = sum(1 for r in ping_rows if r[0].latency_ms and r[0].latency_ms > 100)
    ctx["ping"] = {"total": len(ping_rows), "alive": alive, "dead": dead, "high_latency": high_latency}

    # Traffic volume
    traffic_q = select(
        func.sum(TrafficLog.bytes_total).label("total"),
        func.count().label("connections"),
    )
    if org_id:
        traffic_q = traffic_q.where(TrafficLog.organization_id == org_id)
    tr = (await db.execute(traffic_q)).one()
    ctx["traffic"] = {
        "total_bytes": _format_bytes(tr.total or 0),
        "total_connections": tr.connections or 0,
    }

    # Firewall & Internet rules
    fw_q = select(func.count()).select_from(FirewallRule)
    if org_id:
        fw_q = fw_q.where(FirewallRule.organization_id == org_id)
    ctx["firewall_rules"] = (await db.execute(fw_q)).scalar() or 0

    inet_q = select(func.count()).select_from(InternetRule)
    if org_id:
        inet_q = inet_q.where(InternetRule.organization_id == org_id)
    ctx["internet_rules"] = (await db.execute(inet_q)).scalar() or 0

    # Online computers
    comp_q = select(func.count()).select_from(Computer)
    if org_id:
        comp_q = comp_q.where(Computer.organization_id == org_id)
    ctx["total_computers"] = (await db.execute(comp_q)).scalar() or 0

    online_q = select(func.count()).select_from(Computer)
    if org_id:
        online_q = online_q.where(Computer.organization_id == org_id)
    online_q = online_q.where(Computer.status == "online")
    ctx["online_computers"] = (await db.execute(online_q)).scalar() or 0

    return ctx


def _analyze_question(question: str, ctx: dict) -> dict:
    """Rule-based NLP analysis of common network questions."""
    q = question.lower()
    response_parts = []
    data = {}

    # Detect question type
    if any(w in q for w in ["internet", "sayt", "site", "web", "sekin", "tezlik", "speed", "slow"]):
        if ctx["top_bandwidth_devices"]:
            worst = ctx["top_bandwidth_devices"][0]
            response_parts.append(f"🔴 Eng yuklangan qurilma: **{worst['hostname']}** — oʻrtacha {worst['avg_util_pct']}% yuklanish.")
            if worst['avg_util_pct'] > 80:
                response_parts.append(f"⚠️ Ushbu qurilmada ortiqcha yuklanish mavjud (>{worst['avg_util_pct']}%).")
            for d in ctx["top_bandwidth_devices"]:
                response_parts.append(f"  • {d['hostname']}: {d['avg_util_pct']}% yuklanish, in: {d['avg_in']}, out: {d['avg_out']}")
        else:
            response_parts.append("ℹ️ Hozirda bandwidth ma'lumotlari mavjud emas.")
        data["analysis_type"] = "bandwidth"
        data["severity"] = "high" if any(d["avg_util_pct"] > 80 for d in ctx.get("top_bandwidth_devices", [])) else "normal"

    elif any(w in q for w in ["ping", "latency", "kechikish", "ulanish", "connection", "offline"]):
        ping = ctx.get("ping", {})
        response_parts.append(f"📡 Ping holati: {ping.get('alive', 0)} jonli, {ping.get('dead', 0)} o‘chik, {ping.get('high_latency', 0)} yuqori kechikishli.")
        if ping.get('dead', 0) > 0:
            response_parts.append(f"❌ {ping['dead']} ta qurilma ping bermayapti — tekshirish talab etiladi.")
        if ping.get('high_latency', 0) > 0:
            response_parts.append(f"⚠️ {ping['high_latency']} ta qurilmada kechikish 100ms dan yuqori.")
        data["analysis_type"] = "ping"
        data["severity"] = "high" if ping.get('dead', 0) > 0 else "medium" if ping.get('high_latency', 0) > 0 else "normal"

    elif any(w in q for w in ["qurilma", "device", "switch", "router", "topology", "tarmoq", "network"]):
        devices = ctx.get("devices", {})
        response_parts.append(f"🏗️ Tarmoq qurilmalari: {ctx.get('total_devices', 0)} ta.")
        for dtype, count in sorted(devices.items(), key=lambda x: -x[1]):
            response_parts.append(f"  • {dtype}: {count} ta")
        data["analysis_type"] = "devices"
        data["severity"] = "normal"

    elif any(w in q for w in ["xavfsizlik", "security", "threat", "tahdid", "virus", "xaker"]):
        from app.models.security import ThreatDetection
        # This would need a db query but we don't have db session here
        response_parts.append("🛡️ Xavfsizlik tahlili uchun maxsus so‘rov kerak.")
        data["analysis_type"] = "security"
        data["severity"] = "info"

    elif any(w in q for w in ["kompyuter", "computer", "pc", "online", "holat", "status"]):
        response_parts.append(f"💻 Kompyuterlar: {ctx.get('total_computers', 0)} ta umumiy, {ctx.get('online_computers', 0)} ta online.")
        data["analysis_type"] = "computers"
        data["severity"] = "normal"

    else:
        response_parts.append("🤖 Men tarmoq monitoring tizimi AI yordamchisiman.")
        response_parts.append(f"Hozirda tizimda {ctx.get('total_devices', 0)} ta qurilma, {ctx.get('total_computers', 0)} ta kompyuter kuzatilmoqda.")
        response_parts.append(f"• Tarmoq trafigi: {ctx['traffic']['total_bytes']} ({ctx['traffic']['total_connections']} ulanish)")
        response_parts.append(f"• Firewall: {ctx['firewall_rules']} ta qoida | Internet: {ctx['internet_rules']} ta qoida")
        response_parts.append(f"• Ping: {ctx['ping'].get('alive', 0)} jonli, {ctx['ping'].get('dead', 0)} o‘lik")
        data["analysis_type"] = "general"
        data["severity"] = "info"

    return {"response": "\n\n".join(response_parts), "data": data}


@router.post("/chat")
async def ai_chat(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI Administrator — ask questions about your network in natural language."""
    question = data.get("question", "").strip()
    if not question:
        raise HTTPException(400, "Savol matnini kiriting")

    ctx = await _gather_network_context(db, current_user.organization_id)
    result = _analyze_question(question, ctx)

    return {
        "question": question,
        "answer": result["response"],
        "analysis": result["data"],
        "user": current_user.full_name or current_user.username,
    }


@router.get("/status")
async def ai_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a health summary of the entire system."""
    ctx = await _gather_network_context(db, current_user.organization_id)
    summary = []
    issues = []

    # Check bandwidth
    for d in ctx.get("top_bandwidth_devices", []):
        if d["avg_util_pct"] > 80:
            issues.append(f"🔴 {d['hostname']} — {d['avg_util_pct']}% yuklanish (kritik)")
        elif d["avg_util_pct"] > 60:
            issues.append(f"🟡 {d['hostname']} — {d['avg_util_pct']}% yuklanish")

    # Check ping
    ping = ctx.get("ping", {})
    if ping.get("dead", 0) > 0:
        issues.append(f"❌ {ping['dead']} ta qurilma javob bermayapti")
    if ping.get("high_latency", 0) > 0:
        issues.append(f"⚠️ {ping['high_latency']} ta qurilmada yuqori kechikish")

    # Check online
    if ctx.get("online_computers", 0) < ctx.get("total_computers", 0) * 0.5:
        issues.append(f"💻 Kompyuterlarning 50% dan kami online ({ctx.get('online_computers', 0)}/{ctx.get('total_computers', 0)})")

    overall = "sog'lom" if len(issues) == 0 else "kritik" if any("🔴" in i for i in issues) else "e'tibor talab"
    severity = "normal" if len(issues) == 0 else "high" if any("kritik" in i for i in issues) else "warning"

    return {
        "status": overall,
        "severity": severity,
        "devices": ctx.get("total_devices", 0),
        "computers": {
            "total": ctx.get("total_computers", 0),
            "online": ctx.get("online_computers", 0),
        },
        "traffic": ctx["traffic"]["total_bytes"],
        "ping": ping.get("alive", 0) or 0,
        "issues": [
            {"title": i.split("—")[0].replace("🔴", "").replace("🟡", "").replace("❌", "").replace("⚠️", "").replace("💻", "").strip(), "severity": "high" if "🔴" in i or "❌" in i else "warning" if "🟡" in i or "⚠️" in i else "normal", "description": i}
            for i in issues
        ],
    }
