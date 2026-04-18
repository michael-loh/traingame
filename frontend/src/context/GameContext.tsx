import React, { createContext, useContext, useEffect, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { GameState } from "../types/game";
import { EventType, GameEvent } from "../types/events";
import { mockGameState } from "../mocks/gameState";

interface GameContextType {
  gameState: GameState | null;
  readyState: ReadyState;
  sendEvent: (type: EventType, payload: any) => void;
  error: string | null;
  clearError: () => void;
  playerId: string | null;
  setPlayerId: (id: string) => void;
  gameId: string | null;
  setGameId: (id: string) => void;
  token: string | null;
  setToken: (token: string) => void;
  isDemoMode: boolean;
  storedGameId: string | null;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

const useWebSocketHook: any = (useWebSocket as any).default || useWebSocket;

export const GameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDemoMode] = useState(() => new URLSearchParams(window.location.search).get("demo") === "true");
  
  // 1. Look for a stored session in case they want to rejoin
  const [storedGameId] = useState(() => localStorage.getItem("train_game_id"));

  // 2. ONLY auto-load into the state if in URL or Demo Mode
  const [gameId, setGameId] = useState<string | null>(() => {
    if (isDemoMode) return "demo-123";
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("game");
  });

  const [gameState, setGameState] = useState<GameState | null>(isDemoMode ? mockGameState : null);
  const [error, setError] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(isDemoMode ? "Alice" : localStorage.getItem("train_player_id"));
  const [token, setToken] = useState<string | null>(isDemoMode ? "demo-token" : localStorage.getItem("train_token"));

  const socketUrl = !isDemoMode && gameId && playerId && token 
    ? `ws://localhost:8000/ws/${gameId}/${playerId}?token=${token}` 
    : null;

  const { sendMessage, lastJsonMessage, readyState } = useWebSocketHook(socketUrl, {
    shouldReconnect: () => !isDemoMode,
    reconnectInterval: 3000,
  });

  useEffect(() => {
    if (!isDemoMode && lastJsonMessage) {
      const event = lastJsonMessage as GameEvent;
      if (event.type === EventType.GAME_UPDATE) {
        setGameState(event.payload as GameState);
      } else if (event.type === EventType.ERROR) {
        setError(event.payload.message);
      }
    }
  }, [lastJsonMessage, isDemoMode]);

  useEffect(() => {
    if (!isDemoMode) {
      if (playerId) localStorage.setItem("train_player_id", playerId);
      if (gameId) {
         localStorage.setItem("train_game_id", gameId);
         // Update URL to match current game
         if (!window.location.search.includes(`game=${gameId}`)) {
            window.history.pushState({}, '', `?game=${gameId}`);
         }
      }
      if (token) localStorage.setItem("train_token", token);
    }
  }, [playerId, gameId, token, isDemoMode]);

  const sendEvent = (type: EventType, payload: any) => {
    if (isDemoMode) {
      console.log("DEMO MODE: Event sent", { type, payload });
      return;
    }
    sendMessage(JSON.stringify({ type, payload }));
  };

  const clearError = () => setError(null);

  return (
    <GameContext.Provider
      value={{
        gameState,
        readyState: isDemoMode ? ReadyState.OPEN : readyState,
        sendEvent,
        error,
        clearError,
        playerId,
        setPlayerId,
        gameId,
        setGameId,
        token,
        setToken,
        isDemoMode,
        storedGameId,
      }}
    >
      {children}
    </GameContext.Provider>
  );
};

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error("useGame must be used within a GameProvider");
  }
  return context;
};
