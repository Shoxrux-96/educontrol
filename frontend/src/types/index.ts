export interface User {
  id: string;
  organization_id?: string;
  username: string;
  email: string;
  role: "owner" | "admin" | "viewer";
  full_name?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: User;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  is_active: boolean;
  max_computers: number;
  created_at: string;
  user_count?: number;
  computer_count?: number;
  policy_count?: number;
}

export interface Computer {
  id: string;
  name: string;
  hostname?: string;
  ip_address?: string;
  mac_address?: string;
  group_id?: string;
  group_name?: string;
  status: "online" | "offline" | "busy" | "locked" | "maintenance";
  os_version?: string;
  agent_version?: string;
  cpu_usage?: number;
  ram_usage?: number;
  disk_usage?: number;
  last_seen?: string;
  current_user?: string;
}

export interface ComputerGroup {
  id: string;
  name: string;
  description?: string;
  color?: string;
  computer_count?: number;
}

export interface Policy {
  id: string;
  name: string;
  description?: string;
  policy_type: "internet" | "application" | "usb" | "print_screen";
  config: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
}

export interface Command {
  id: string;
  computer_id: string;
  computer_name?: string;
  command_type: string;
  payload?: Record<string, unknown>;
  status: "pending" | "sent" | "delivered" | "executed" | "failed";
  sent_at: string;
  executed_at?: string;
  result?: Record<string, unknown>;
}

export interface AuditLog {
  id: number;
  event_type: string;
  severity: "info" | "warning" | "critical";
  computer_id?: string;
  user_id?: string;
  description: string;
  created_at: string;
}

export interface DashboardStats {
  total_computers: number;
  online_computers: number;
  offline_computers: number;
  total_users: number;
  active_policies: number;
  alerts_today: number;
  commands_today: number;
}

export interface AlertEvent {
  id: string;
  rule_id: string;
  rule_name: string;
  metric: string;
  actual_value: number;
  threshold: number;
  triggered_at: string;
  acknowledged: boolean;
  acknowledged_by?: string;
}

export interface AlertRule {
  id: string;
  name: string;
  metric: string;
  condition: string;
  threshold: number;
  enabled: boolean;
  notification_channels: string[];
  cooldown_minutes: number;
  last_triggered?: string;
}

export interface Message {
  id: string;
  title?: string;
  body: string;
  message_type: "info" | "warning" | "critical";
  target_type: "computer" | "group" | "all";
  target_id?: string;
  sent_at: string;
}
