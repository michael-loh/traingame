import React from "react";
import { useGame } from "../context/GameContext";
import { EventType } from "../types/events";

export const DrawPiles: React.FC = () => {
  const { gameState, sendEvent, playerId } = useGame();

  if (!gameState) return null;

  const isPlayersTurn = gameState.turn_order[gameState.current_turn_index] === playerId;

  const handleDrawBlind = () => {
    if (!isPlayersTurn) return;
    sendEvent(EventType.DRAW_TRAIN_CARD, { card_id: null });
  };

  const handleDrawGoals = () => {
    if (!isPlayersTurn) return;
    sendEvent(EventType.DRAW_GOAL_CARDS, {});
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700 h-full flex flex-col shadow-lg overflow-hidden">
      <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Draw</h2>
      <div className="flex-1 flex gap-3">
        <button
          onClick={handleDrawBlind}
          disabled={!isPlayersTurn}
          className={`flex-1 rounded-xl flex flex-col items-center justify-center gap-1 transition-all border-2 ${
            isPlayersTurn 
              ? "bg-slate-900 border-indigo-500 hover:bg-black hover:border-indigo-400 active:scale-95 shadow-indigo-500/20 shadow-lg" 
              : "bg-slate-900 border-slate-700 opacity-50 cursor-not-allowed"
          }`}
        >
          <span className="text-white text-[10px] font-black uppercase tracking-widest">Trains</span>
          <span className="text-slate-500 text-[8px] font-bold uppercase">{gameState.train_deck_count || "?"} Left</span>
        </button>
        <button
          onClick={handleDrawGoals}
          disabled={!isPlayersTurn}
          className={`flex-1 rounded-xl flex flex-col items-center justify-center gap-1 transition-all border-2 ${
            isPlayersTurn 
              ? "bg-slate-100 border-slate-200 text-slate-900 hover:bg-white hover:border-white active:scale-95 shadow-white/10 shadow-lg" 
              : "bg-slate-900 border-slate-700 opacity-50 cursor-not-allowed"
          }`}
        >
          <span className="text-[10px] font-black uppercase tracking-widest">Goals</span>
          <span className="text-slate-400 text-[8px] font-bold uppercase">{gameState.goal_deck_count || "?"} Left</span>
        </button>
      </div>
    </div>
  );
};
