"use client";

import { useState, useEffect, createContext, useContext, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { api } from "../lib/api-client";

interface User {
  id: number;
  email: string;
  name: string;
  company?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string, company?: string) => Promise<void>;
  logout: () => void;
  checkSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const logout = () => {
    localStorage.removeItem("auth_token");
    setUser(null);
    router.push("/login");
  };

  const checkSession = async () => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      if (pathname !== "/login" && pathname !== "/signup") {
        router.push("/login");
      }
      return;
    }

    try {
      const userData = await api.me();
      setUser(userData);
    } catch (err) {
      // Token is invalid/expired
      localStorage.removeItem("auth_token");
      setUser(null);
      if (pathname !== "/login" && pathname !== "/signup") {
        router.push("/login");
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const data = await api.login({ email, password });
      localStorage.setItem("auth_token", data.access_token);
      setUser(data.user);
      router.push("/dashboard");
    } catch (err) {
      setLoading(false);
      throw err;
    }
  };

  const signup = async (name: string, email: string, password: string, company?: string) => {
    setLoading(true);
    try {
      await api.signup({ name, email, password, company });
      // Automatically login after signup
      await login(email, password);
    } catch (err) {
      setLoading(false);
      throw err;
    }
  };

  useEffect(() => {
    checkSession();
  }, [pathname]);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, checkSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
