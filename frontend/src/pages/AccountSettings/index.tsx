import { Outlet } from 'react-router-dom';
import { AccountTabs } from './Tabs';
import { cn } from "@/lib/utils";

export default function AccountSettings() {
  return (
    <div className={cn("space-y-6")}>
      <div>
        <h1 className="text-2xl font-bold tracking-wider bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
          Mein Konto
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Verwalten Sie Ihre Kontoeinstellungen und Abonnements
        </p>
      </div>
      <AccountTabs />
      <div className="mt-6">
        <Outlet />
      </div>
    </div>
  );
}
