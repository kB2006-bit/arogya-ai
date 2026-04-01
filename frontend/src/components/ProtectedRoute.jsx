import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAppContext } from "@/context/AppContext";


export const ProtectedRoute = () => {
  const location = useLocation();
  const { isAuthenticated } = useAppContext();

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return <Outlet />;
};