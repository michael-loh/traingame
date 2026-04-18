import React from "react";
import { useGame } from "../context/GameContext";

export const HUD: React.FC = () => {
  const { gameState } = useGame();

  if (!gameState) return null;

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white">
      <div className="p-3 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Scoreboard</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {gameState.turn_order.map((pId, idx) => {
          const p = gameState.players[pId];
          const isCurrent = gameState.current_turn_index === idx;
          return (
            <div
              key={pId}
              className={`p-3 border-b border-slate-800 transition-all ${
                isCurrent ? "bg-indigo-600/20 border-l-4 border-l-indigo-500" : "opacity-60"
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-bold truncate">{pId}</span>
                {isCurrent && <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />}
              </div>
              <div className="grid grid-cols-3 gap-1 text-[9px] font-bold text-slate-400 uppercase tracking-tighter">
                <div className="flex flex-col">
                  <span>Score</span>
                  <span className="text-white text-xs">{p.score}</span>
                </div>
                <div className="flex flex-col">
                  <span>Cars</span>
                  <span className="text-white text-xs">{p.train_cars_remaining}</span>
                </div>
                <div className="flex flex-col text-right">
                  <span>Hand</span>
                  <span className="text-white text-xs">{p.hand.length}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
