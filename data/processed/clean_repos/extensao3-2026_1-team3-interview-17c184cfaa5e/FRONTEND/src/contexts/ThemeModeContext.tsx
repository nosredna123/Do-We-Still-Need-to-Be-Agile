import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";

type ThemeMode = "light" | "dark";

type ThemeModeContextData = {
  mode: ThemeMode;
  toggleTheme: () => void;
};

const ThemeModeContext = createContext<ThemeModeContextData | undefined>(
  undefined
);

type Props = {
  children: ReactNode;
};

export function ThemeModeProvider({ children }: Props) {
  const [mode, setMode] = useState<ThemeMode>("light");

  const toggleTheme = () => {
    setMode((prev) => (prev === "light" ? "dark" : "light"));
  };

  const theme = useMemo(() => {
    return createTheme({
      palette: {
        mode,
        background: {
          default: mode === "light" ? "#f8fafc" : "#111827",
          paper: mode === "light" ? "#ffffff" : "#1f2937",
        },
        primary: {
          main: "#9cbde8",
        },
        secondary: {
          main: "#a7e5cb",
        },
        success: {
          main: "#2d5c48",
        },
        text: {
          primary: mode === "light" ? "#111827" : "#f9fafb",
          secondary: mode === "light" ? "#6b7280" : "#d1d5db",
        },
      },
      shape: {
        borderRadius: 16,
      },
      typography: {
        fontFamily: `"Roboto", "Helvetica", "Arial", sans-serif`,
      },
    });
  }, [mode]);

  return (
    <ThemeModeContext.Provider value={{ mode, toggleTheme }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
}

export function useThemeMode() {
  const context = useContext(ThemeModeContext);

  if (!context) {
    throw new Error("useThemeMode must be used within ThemeModeProvider");
  }

  return context;
}