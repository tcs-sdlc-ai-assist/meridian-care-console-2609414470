export type Role = 'coordinator' | 'supervisor' | 'auditor';
export interface User { coordinator_id: string; name: string; email: string; role: Role; }
export interface LoginResponse { access_token: string; token_type: 'bearer'; user: User; }
export interface Metric { label: string; value: number; }
export interface DashboardData { metrics: Metric[]; attention: string[]; activity: string[]; chart: number[]; }
export interface MemberRow { member_id: string; name: string; dob: string; plan: string; pcp: string; risk_level: string; open_gaps: number; coordinator_id: string; }
export interface MemberList { items: MemberRow[]; total: number; }
