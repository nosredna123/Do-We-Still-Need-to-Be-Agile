import type { Role } from "../roles.ts";

declare global {
    namespace Express {
      interface Request {
        auth?: {
          id: number;
          userRole: Role; // ou Role, se você tiver um tipo para isso
        }
      }
    }
  }
  