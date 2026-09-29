import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export type FeatureFlag = {
  id: number;
  name: string;
  key: string;
  description?: string;
  default_enabled: boolean;
  is_archived?: boolean;
  created_by?: number;
  created_at?: string;
  updated_at?: string;
};

export type Environment = {
  id: number;
  name: string;
  description?: string;
};

export type Assignment = {
  id: number;
  feature_flag_id: number;
  user_id: number;
  enabled: boolean;
  reason?: string;
  created_at?: string;
};

export const endpoints = {
  login: "/auth/login",
  me: "/auth/me",
  users: "/users",
  roles: "/users/roles",
  environments: "/environments",
  flags: "/feature-flags",
  evaluate: "/evaluate",
  audit: "/audit-logs",
  summary: "/dashboard/summary",
  topFlags: "/dashboard/top-flags",
  analytics: (id: number) => `/dashboard/analytics/${id}`,
  rollout: (flagId: number, envId: number) => `/feature-flags/${flagId}/rollouts/${envId}`,
  rollback: (flagId: number, envId: number) => `/feature-flags/${flagId}/rollouts/${envId}/rollback`,
  assignments: (flagId: number) => `/feature-flags/${flagId}/assignments`,
  assignment: (flagId: number, assignmentId: number) => `/feature-flags/${flagId}/assignments/${assignmentId}`
};
