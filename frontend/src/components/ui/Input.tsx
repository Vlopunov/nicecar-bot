import { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export function Input({ label, className = '', ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm text-[var(--hint-color)]">{label}</label>}
      <input
        className={`w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition ${className}`}
        {...props}
      />
    </div>
  )
}

export function Textarea({ label, className = '', ...props }: { label?: string } & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm text-[var(--hint-color)]">{label}</label>}
      <textarea
        className={`w-full px-4 py-3 rounded-xl bg-[var(--secondary-bg)] text-[var(--text-color)] border-none outline-none focus:ring-2 focus:ring-accent/30 transition resize-none ${className}`}
        rows={3}
        {...props}
      />
    </div>
  )
}
