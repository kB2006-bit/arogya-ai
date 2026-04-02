import "@/App.css";
import { ThemeProvider } from "next-themes";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/AppShell";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Toaster } from "@/components/ui/sonner";
import { AppProvider, useAppContext } from "@/context/AppContext";
import AuthPage from "@/pages/AuthPage";
import ClinicsPage from "@/pages/ClinicsPage";
import DashboardPage from "@/pages/DashboardPage";
import HistoryPage from "@/pages/HistoryPage";
import LandingPage from "@/pages/LandingPage";


const AppRoutes = () => {
  const { isAuthenticated } = useAppContext();

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route element={isAuthenticated ? <Navigate replace to="/dashboard" /> : <LandingPage />} path="/" />
        <Route element={isAuthenticated ? <Navigate replace to="/dashboard" /> : <AuthPage mode="login" />} path="/login" />
        <Route element={isAuthenticated ? <Navigate replace to="/dashboard" /> : <AuthPage mode="signup" />} path="/signup" />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardPage />} path="/dashboard" />
          <Route element={<Navigate replace to="/dashboard" />} path="/chat" />
          <Route element={<ClinicsPage />} path="/clinics" />
          <Route element={<HistoryPage />} path="/history" />
        </Route>
      </Route>
    </Routes>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        <AppProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
          <Toaster position="top-right" />
        </AppProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
