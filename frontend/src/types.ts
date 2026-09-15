export type Role = 'coordinator' | 'supervisor' | 'auditor';
export interface User { coordinator_id: string; name: string; email: string; role: Role; }
export interface LoginResponse { access_token: string; token_type: 'bearer'; user: User; }
