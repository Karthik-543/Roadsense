import { AuthResponse, Assessment, User } from '../types';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'https://roadsense-1-j77g.onrender.com').replace(/\/$/, '');
const API_BASE = `${BASE_URL}/api`;

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function register(email: string, password: string, fullName: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, fullName }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'Registration failed' }));
    throw new Error(err.message || 'Registration failed');
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'Login failed' }));
    throw new Error(err.message || 'Invalid email or password');
  }
  return res.json();
}

export async function getCurrentUser(): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Unauthorized');
  }
  return res.json();
}

export async function createAssessment(
  file: File,
  latitude?: number | null,
  longitude?: number | null,
  threshold = 0.3
): Promise<Assessment> {
  const formData = new FormData();
  formData.append('file', file);
  if (latitude !== undefined && latitude !== null) {
    formData.append('latitude', latitude.toString());
  }
  if (longitude !== undefined && longitude !== null) {
    formData.append('longitude', longitude.toString());
  }
  formData.append('threshold', threshold.toString());

  const res = await fetch(`${API_BASE}/assessments`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'Assessment creation failed' }));
    throw new Error(err.message || 'Assessment processing failed');
  }

  return res.json();
}

export async function addAdditionalImage(
  assessmentId: string,
  file: File,
  threshold = 0.3
): Promise<Assessment> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('threshold', threshold.toString());

  const res = await fetch(`${API_BASE}/assessments/${assessmentId}/images`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'Failed to add image' }));
    throw new Error(err.message || 'Failed to attach image');
  }

  return res.json();
}

export async function getUserAssessments(): Promise<Assessment[]> {
  const res = await fetch(`${API_BASE}/assessments`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch user assessments');
  }
  return res.json();
}

export async function getAssessmentDetails(assessmentId: string): Promise<Assessment> {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch assessment details');
  }
  return res.json();
}

export async function askRoadSense(question: string, assessmentId?: string, ragMode?: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ question, assessmentId, ragMode }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: 'Chat request failed' }));
    throw new Error(err.message || 'Chat service unavailable');
  }
  return res.json();
}
