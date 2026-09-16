import React, { createContext, useContext, useMemo, useState } from 'react';
import { Backdrop, CircularProgress, Typography, Box } from '@mui/material';

type LoadingContextType = {
  openLoading: (message?: string) => void;
  closeLoading: () => void;
  isLoading: boolean;
};

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const LoadingProvider = ({ children }: { children: React.ReactNode }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('Processando...');

  const openLoading = (customMessage = 'Processando...') => {
    setMessage(customMessage);
    setIsLoading(true);
  };

  const closeLoading = () => {
    setIsLoading(false);
    setMessage('Processando...');
  };

  const value = useMemo(
    () => ({
      openLoading,
      closeLoading,
      isLoading,
    }),
    [isLoading]
  );

  return (
    <LoadingContext.Provider value={value}>
      {children}

      <Backdrop
        open={isLoading}
        sx={(theme) => ({
          color: '#fff',
          zIndex: theme.zIndex.modal + 1,
          flexDirection: 'column',
          gap: 2,
        })}
      >
        <CircularProgress color="inherit" />
        <Box>
          <Typography variant="h6">{message}</Typography>
        </Box>
      </Backdrop>
    </LoadingContext.Provider>
  );
};

export const useLoading = () => {
  const context = useContext(LoadingContext);

  if (!context) {
    throw new Error('useLoading deve ser usado dentro de LoadingProvider');
  }

  return context;
};