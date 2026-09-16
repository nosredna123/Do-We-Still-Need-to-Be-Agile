import { createEnv } from '@t3-oss/env-core'
import { z } from 'zod'

export const Env = createEnv({
  clientPrefix: 'VITE_',
  client: {
    VITE_API_BASE_URL: z.string().refine(
      (v) => {
        try {
          new URL(v)
          return true
        } catch {
          return false
        }
      },
      { message: 'Invalid URL' }
    ),
  },
  runtimeEnv: import.meta.env,
  emptyStringAsUndefined: true,
})
