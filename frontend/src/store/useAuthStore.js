import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  token: null,
  role: null,
  email: null,
  isAuthenticated: false,

  login: (email, token, role) => {
    localStorage.setItem('lms_token', token);
    localStorage.setItem('lms_role', role);
    localStorage.setItem('lms_email', email);
    set({ token, role, email, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('lms_token');
    localStorage.removeItem('lms_role');
    localStorage.removeItem('lms_email');
    set({ token: null, role: null, email: null, isAuthenticated: false });
  },

  initialize: () => {
    const token = localStorage.getItem('lms_token');
    const role = localStorage.getItem('lms_role');
    const email = localStorage.getItem('lms_email');

    if (token && role && email) {
      set({ token, role, email, isAuthenticated: true });
    }
  }
}));
