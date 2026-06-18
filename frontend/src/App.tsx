import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, useAuth } from "./api/AuthContext";
import Layout from "./components/Layout";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import OwnerDashboard from "./pages/OwnerDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import ViewerDashboard from "./pages/ViewerDashboard";
import ComputersPage from "./pages/ComputersPage";
import GroupsPage from "./pages/GroupsPage";
import PoliciesPage from "./pages/PoliciesPage";
import CommandsPage from "./pages/CommandsPage";
import MessagesPage from "./pages/MessagesPage";
import AuditPage from "./pages/AuditPage";
import MonitoringPage from "./pages/MonitoringPage";
import ReportsPage from "./pages/ReportsPage";
import OrganizationsPage from "./pages/OrganizationsPage";
import SettingsPage from "./pages/SettingsPage";
import InternetRules from "./pages/InternetRules";
import FirewallRules from "./pages/FirewallRules";
import TrafficMonitoring from "./pages/TrafficMonitoring";
import HelpDeskTickets from "./pages/HelpDeskTickets";
import VpnPage from "./pages/VpnPage";
import NetworkTopology from "./pages/NetworkTopology";
import IpManagement from "./pages/IpManagement";
import PingMonitoring from "./pages/PingMonitoring";
import BandwidthMonitoring from "./pages/BandwidthMonitoring";
import ActiveDirectory from "./pages/ActiveDirectory";
import GroupPolicy from "./pages/GroupPolicy";
import RemoteDesktop from "./pages/RemoteDesktop";
import SoftwareManagement from "./pages/SoftwareManagement";
import SecurityDashboard from "./pages/SecurityDashboard";
import UsbControl from "./pages/UsbControl";
import AntivirusMonitoring from "./pages/AntivirusMonitoring";
import LoginAudit from "./pages/LoginAudit";
import ExamsPage from "./pages/ExamsPage";
import AiAssistant from "./pages/AiAssistant";
import SyslogServer from "./pages/SyslogServer";
import SnmpMonitoring from "./pages/SnmpMonitoring";
import BackupManager from "./pages/BackupManager";

function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

function RoleDashboard() {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role === "owner") return <OwnerDashboard />;
  if (user?.role === "admin") return <AdminDashboard />;
  return <ViewerDashboard />;
}

function OwnerRoute() {
  const { isAuthenticated, isOwner } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isOwner) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<RoleDashboard />} />
          <Route path="/computers" element={<ComputersPage />} />
          <Route path="/groups" element={<GroupsPage />} />
          <Route path="/policies" element={<PoliciesPage />} />
          <Route path="/commands" element={<CommandsPage />} />
          <Route path="/messages" element={<MessagesPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/monitoring" element={<MonitoringPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route element={<OwnerRoute />}>
            <Route path="/organizations" element={<OrganizationsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="/internet" element={<InternetRules />} />
          <Route path="/firewall" element={<FirewallRules />} />
          <Route path="/traffic" element={<TrafficMonitoring />} />
          <Route path="/helpdesk" element={<HelpDeskTickets />} />
          <Route path="/vpn" element={<VpnPage />} />
          <Route path="/network/topology" element={<NetworkTopology />} />
          <Route path="/network/ip" element={<IpManagement />} />
          <Route path="/network/ping" element={<PingMonitoring />} />
          <Route path="/network/bandwidth" element={<BandwidthMonitoring />} />
          <Route path="/ad" element={<ActiveDirectory />} />
          <Route path="/ad/gpo" element={<GroupPolicy />} />
          <Route path="/remote-desktop/:computerId" element={<RemoteDesktop />} />
          <Route path="/software/:computerId" element={<SoftwareManagement />} />
          <Route path="/software" element={<SoftwareManagement />} />
          <Route path="/security" element={<SecurityDashboard />} />
          <Route path="/security/usb" element={<UsbControl />} />
          <Route path="/security/antivirus" element={<AntivirusMonitoring />} />
          <Route path="/security/logins" element={<LoginAudit />} />
          <Route path="/education/exams" element={<ExamsPage />} />
          <Route path="/ai" element={<AiAssistant />} />
          <Route path="/enterprise/syslog" element={<SyslogServer />} />
          <Route path="/enterprise/snmp" element={<SnmpMonitoring />} />
          <Route path="/enterprise/backup" element={<BackupManager />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
