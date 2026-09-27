import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldAlert, PlusCircle, LayoutDashboard, MessageSquare, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-slate-950/80 backdrop-blur border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-500/30">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              RoadSense AI
            </span>
            <span className="block text-[10px] text-slate-400 tracking-wider uppercase font-semibold">
              Evidence-Aware RAG Subsystem
            </span>
          </div>
        </Link>

        <nav className="flex items-center space-x-4">
          <Link
            to="/report"
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-blue-600/20"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Report Road Damage</span>
          </Link>

          <Link
            to="/ask"
            className="flex items-center space-x-1.5 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg text-sm transition"
          >
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            <span>Ask RoadSense</span>
          </Link>

          {user ? (
            <>
              <Link
                to="/dashboard"
                className="flex items-center space-x-1.5 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg text-sm transition"
              >
                <LayoutDashboard className="w-4 h-4 text-blue-400" />
                <span>Dashboard</span>
              </Link>

              <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
                <Link to="/profile" className="flex items-center space-x-2 text-sm text-slate-300 hover:text-white">
                  <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400 font-bold">
                    {user.fullName ? user.fullName[0].toUpperCase() : 'U'}
                  </div>
                </Link>

                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 rounded-lg transition"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <Link
                to="/login"
                className="px-3 py-2 text-sm text-slate-300 hover:text-white font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium border border-slate-700 transition"
              >
                Register
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};
