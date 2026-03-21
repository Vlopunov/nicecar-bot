import { useState } from 'react'
import type { PortfolioItem } from '../../types'

interface Props {
  items: PortfolioItem[]
}

export function PortfolioGallery({ items }: Props) {
  const [selected, setSelected] = useState<PortfolioItem | null>(null)

  return (
    <>
      <div className="grid grid-cols-2 gap-2">
        {items.map(item => (
          <div
            key={item.id}
            className="aspect-square rounded-xl overflow-hidden cursor-pointer relative"
            onClick={() => setSelected(item)}
          >
            <img
              src={item.image_url}
              alt={item.description || ''}
              className="w-full h-full object-cover"
              loading="lazy"
            />
            {item.car_brand && (
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 p-2">
                <p className="text-white text-xs">{item.car_brand} {item.car_model}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Lightbox */}
      {selected && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div className="max-w-full max-h-full" onClick={e => e.stopPropagation()}>
            <img
              src={selected.image_url}
              alt=""
              className="max-w-full max-h-[80vh] object-contain rounded-xl"
            />
            <div className="text-white text-center mt-4">
              {selected.car_brand && <p className="font-semibold">{selected.car_brand} {selected.car_model}</p>}
              {selected.description && <p className="text-sm text-gray-300 mt-1">{selected.description}</p>}
            </div>
          </div>
          <button
            className="absolute top-4 right-4 text-white text-3xl"
            onClick={() => setSelected(null)}
          >
            ×
          </button>
        </div>
      )}
    </>
  )
}
