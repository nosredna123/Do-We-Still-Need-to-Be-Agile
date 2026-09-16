import { Card, CardContent } from "../components/ui/card";
import { ArrowUpRight, ArrowDownRight, Wallet, TrendingUp, TrendingDown, RefreshCw } from "lucide-react";
import { cn } from "../lib/utils";

interface MetricCardProps {
    title: string;
    value: string;
    change: string;
    trend: "up" | "down" | "neutral";
    icon: "wallet" | "income" | "expense" | "savings";
}

const icons = {
  wallet: Wallet,
  income: TrendingUp,
  expense: TrendingDown,
  savings: RefreshCw,
};

const MetricCard = ({ title, value, change, trend, icon }: MetricCardProps) => {
    const Icon = icons[icon];

    return (
        <Card className="border-border/50 hover:border-primary/20 transition-colors">
            <CardContent className="p-6">
                <div className="flex items-start justify-between">
                <div className="space-y-2">
                    <p className="text-sm text-muted-foreground font-medium">{title}</p>
                    <p className="text-3xl font-bold text-foreground">{value}</p>
                    <div className="flex items-center gap-1">
                    {trend === "up" && <ArrowUpRight className="w-4 h-4 text-[#52c41a]" />}
                    {trend === "down" && <ArrowDownRight className="w-4 h-4 text-[#ff4d4f]" />}
                    <span
                        className={cn(
                        "text-sm font-medium",
                        trend === "up" && "text-[#52c41a]",
                        trend === "down" && "text-[#ff4d4f]",
                        trend === "neutral" && "text-muted-foreground"
                        )}
                    >
                        {change}
                    </span>
                    </div>
                </div>
                <div className="rounded-lg bg-primary/10 p-3">
                    <Icon className="w-6 h-6 text-primary" />
                </div>
                </div>
            </CardContent>
        </Card>

    );
};

export default MetricCard;