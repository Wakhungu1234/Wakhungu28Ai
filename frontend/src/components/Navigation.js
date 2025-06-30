import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    {
      id: "dashboard",
      label: "Trading Analysis",
      icon: "📊",
      path: "/dashboard",
      description: "Live market analysis & predictions"
    },
    {
      id: "bot",
      label: "Basic Bot",
      icon: "🤖",
      path: "/bot", 
      description: "Simple bot management"
    },
    {
      id: "advanced-bot",
      label: "Pro Bot",
      icon: "⚡",
      path: "/advanced-bot", 
      description: "High-frequency AI trading bot"
    }
  ];

  return (
    <nav className="flex space-x-2">
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        
        return (
          <Link
            key={item.id}
            to={item.path}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${isActive 
                ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25' 
                : 'text-gray-300 hover:text-white hover:bg-white/10'
              }
            `}
          >
            <span className="mr-2">{item.icon}</span>
            <span className="hidden md:inline">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
};

export default Navigation;