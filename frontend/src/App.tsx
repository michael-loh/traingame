import { GameProvider, useGame } from "./context/GameContext";
import { GameBoard } from "./components/GameBoard";
import { GameLobby } from "./components/GameLobby";
import { SetupModal } from "./components/SetupModal";
import { HUD } from "./components/HUD";
import { GoalSection } from "./components/GoalSection";
import { MarketBoard } from "./components/MarketBoard";
import { DrawPiles } from "./components/DrawPiles";
import { PlayerHand } from "./components/PlayerHand";
import { GameStatus } from "./types/game";

function GameContainer() {
  const { gameState, error, clearError } = useGame();

  if (!gameState || gameState.status === GameStatus.LOBBY) {
    return (
      <div className="h-screen bg-slate-50 flex items-center justify-center p-4">
        <GameLobby />
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-slate-900 flex flex-col overflow-hidden">
      {/* 1. Global Status Bar (Fills HUD/F space in spirit) */}
      <div className="h-10 bg-black flex items-center justify-between px-6 border-b border-slate-800 flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-[10px] font-black text-white tracking-[0.3em]">TRAIN GAME</span>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2 border-l border-slate-800">
            Game ID: {gameState.game_id}
          </span>
        </div>
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
           <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Live Sync Active</span>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-4 gap-4 min-h-0">
        {/* 2. Top Section: Map & HUD (A & F) */}
        <div className="flex-1 flex gap-4 min-h-0">
          <div className="flex-[4] min-w-0">
            <GameBoard />
          </div>
          <div className="w-64 flex-shrink-0 bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
            <HUD />
          </div>
        </div>

        {/* 3. Middle Section: Actions (B, C, D) */}
        <div className="h-40 flex-shrink-0 flex gap-4">
          <div className="w-64 flex-shrink-0">
            <GoalSection />
          </div>
          <div className="flex-1 min-w-0">
            <MarketBoard />
          </div>
          <div className="w-64 flex-shrink-0">
            <DrawPiles />
          </div>
        </div>

        {/* 4. Bottom Section: Hand (E) */}
        <div className="h-44 flex-shrink-0">
          <PlayerHand />
        </div>
      </div>

      {gameState.status === GameStatus.SETUP && <SetupModal />}

      {error && (
        <div className="fixed top-12 left-1/2 -translate-x-1/2 bg-red-600 text-white px-6 py-2 rounded-full shadow-2xl z-[100] flex items-center gap-4 animate-in slide-in-from-top">
          <span className="text-xs font-bold uppercase tracking-tight">{error}</span>
          <button onClick={clearError} className="bg-white/20 hover:bg-white/30 px-2 py-0.5 rounded-full text-[10px] font-black uppercase">OK</button>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <GameProvider>
      <GameContainer />
    </GameProvider>
  );
}

export default App;
