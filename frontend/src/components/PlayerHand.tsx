import React from "react";
import { useGame } from "../context/GameContext";
import { TrainColor } from "../types/game";

const COLOR_MAP: Record<TrainColor, string> = {
  [TrainColor.RED]: "#f87171",
  [TrainColor.BLUE]: "#60a5fa",
  [TrainColor.GREEN]: "#4ade80",
  [TrainColor.YELLOW]: "#facc15",
  [TrainColor.BLACK]: "#44403c",
  [TrainColor.WHITE]: "#f1f5f9",
  [TrainColor.ORANGE]: "#fb923c",
  [TrainColor.PINK]: "#f472b6",
  [TrainColor.WILD]: "linear-gradient(135deg, #6366f1, #a855f7, #ec4899)",
};

export const PlayerHand: React.FC = () => {
  const { gameState, playerId } = useGame();

  if (!gameState || !playerId) return null;

  const player = gameState.players[playerId];
  if (!player) return null;

  return (
    <div className="bg-slate-900 h-full rounded-2xl p-4 shadow-xl flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Your Cards ({player.hand.length})</span>
      </div>
      <div className="flex-1 flex -space-x-12 hover:space-x-2 transition-all duration-500 overflow-x-auto overflow-y-hidden pt-2 scrollbar-hide">
        {player.hand.map((card, idx) => (
          <div
            key={card.id || idx}
            className="flex-shrink-0 w-20 h-28 rounded-xl border border-white/20 shadow-lg cursor-pointer transition-all hover:-translate-y-4 hover:z-50 relative group"
            style={{ 
              background: card.color === TrainColor.WILD ? COLOR_MAP[TrainColor.WILD] : COLOR_MAP[card.color],
            }}
          >
            <div className="absolute top-2 left-2 w-2 h-2 rounded-full bg-white/30" />
            <div className="absolute bottom-2 right-2 text-[7px] font-black text-white/50 uppercase tracking-tighter">
              {card.color}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
