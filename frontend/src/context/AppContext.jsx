import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, withAuth } from "@/lib/api";


const AppContext = createContext(null);


export const AppProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem("arogya-token") || "");
  const [user, setUser] = useState(() => {
    const rawUser = localStorage.getItem("arogya-user");
    return rawUser ? JSON.parse(rawUser) : null;
  });
  const [language, setLanguage] = useState(() => localStorage.getItem("arogya-language") || "en");

  const persistAuth = useCallback((payload) => {
    setToken(payload.token);
    setUser(payload.user);
    setLanguage((currentLanguage) => currentLanguage || payload.user.language || "en");
    localStorage.setItem("arogya-token", payload.token);
    localStorage.setItem("arogya-user", JSON.stringify(payload.user));
  }, []);

  const clearAuth = useCallback(() => {
    setToken("");
    setUser(null);
    localStorage.removeItem("arogya-token");
    localStorage.removeItem("arogya-user");
  }, []);

  const login = useCallback(async ({ email, password }) => {
    const response = await api.post("/auth/login", { email, password });
    persistAuth(response.data);
    return response.data;
  }, [persistAuth]);

  const signup = useCallback(async ({ email, password }) => {
    const response = await api.post("/auth/signup", { email, password, language });
    persistAuth(response.data);
    return response.data;
  }, [language, persistAuth]);

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  const switchLanguage = useCallback((nextLanguage) => {
    setLanguage(nextLanguage);
    localStorage.setItem("arogya-language", nextLanguage);
  }, []);

  useEffect(() => {
    localStorage.setItem("arogya-language", language);
  }, [language]);

  useEffect(() => {
    const validateSession = async () => {
      if (!token) {
        return;
      }

      try {
        const response = await api.get("/auth/me", withAuth(token));
        setUser(response.data);
        localStorage.setItem("arogya-user", JSON.stringify(response.data));
      } catch (error) {
        clearAuth();
      }
    };

    validateSession();
  }, [token, clearAuth]);

  const value = useMemo(
    () => ({
      token,
      user,
      language,
      isAuthenticated: Boolean(token && user),
      login,
      signup,
      logout,
      switchLanguage,
    }),
    [token, user, language, login, signup, logout, switchLanguage],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};


export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return context;
};