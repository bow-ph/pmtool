import { Link, useLocation } from 'react-router-dom';
import { cn } from "@/lib/utils";
import { UserCircle, Package, Shield } from 'lucide-react';

const tabs = [
  { name: 'Profil', href: '/account', icon: UserCircle },
  { name: 'Pakete', href: '/account/packages', icon: Package },
  { name: 'Sicherheit', href: '/account/security', icon: Shield },
] as const;

export function AccountTabs() {
  const location = useLocation();

  return (
    <div className="border-b">
      <nav className="-mb-px flex space-x-8" aria-label="Tabs">
        {tabs.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-2 py-4 px-1 border-b-2 text-sm font-medium transition-colors",
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
