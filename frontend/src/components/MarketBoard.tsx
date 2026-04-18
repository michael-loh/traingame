import React from "react";
import { useGame } from "../context/GameContext";
import { EventType } from "../types/events";
import { TrainColor } from "../types/game";
import type { TrainCard } from "../types/game";

const COLOR_MAP: Record<TrainColor, string> = {
  [TrainColor.RED]: "#ef4444",
  [TrainColor.BLUE]: "#3b82f6",
  [TrainColor.GREEN]: "#22c55e",
  [TrainColor.YELLOW]: "#eab308",
  [TrainColor.BLACK]: "#000000",
  [TrainColor.WHITE]: "#ffffff",
  [TrainColor.ORANGE]: "#f97316",
  [TrainColor.PINK]: "#ec4899",
  [TrainColor.WILD]: "linear-gradient(45deg, #6366f1, #a855f7, #ec4899)",
};

export const MarketBoard: React.FC = () => {
  const { gameState, sendEvent, playerId } = useGame();

  if (!gameState) return null;

  const isPlayersTurn = gameState.turn_order[gameState.current_turn_index] === playerId;

  const handleDrawFaceUp = (cardId: string) => {
    if (!isPlayersTurn) return;
    sendEvent(EventType.DRAW_TRAIN_CARD, { card_id: cardId });
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700 h-full flex flex-col shadow-lg overflow-hidden">
      <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Market</h2>
      <div className="flex-1 flex gap-3">
        {gameState.face_up_trains.map((card: TrainCard, idx: number) => (
          <div
            key={card.id || idx}
            onClick={() => handleDrawFaceUp(card.id)}
            className={`flex-1 rounded-xl shadow-lg border border-white/10 transition-all relative overflow-hidden group cursor-pointer ${
              isPlayersTurn ? "hover:scale-105 active:scale-95" : "opacity-40 grayscale"
            }`}
            style={{ 
              background: card.color === TrainColor.WILD ? COLOR_MAP[TrainColor.WILD] : COLOR_MAP[card.color]
            }}
          >
            <div className="absolute top-2 left-2 w-2 h-2 rounded-full bg-white/30" />
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
               <span className={`text-[8px] font-black px-2 py-0.5 rounded shadow ${
                 card.color === TrainColor.WHITE ? "text-slate-900 bg-black/5" : "text-white bg-black/30"
               }`}>{card.color.toUpperCase()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
