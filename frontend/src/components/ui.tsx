import type { ButtonHTMLAttributes, ReactNode } from 'react';
export function Button({ children, variant = 'primary', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' }): JSX.Element { return <button className={`button button-${variant}`} {...props}>{children}</button>; }
export function Card({ children }: { children: ReactNode }): JSX.Element { return <section className="card">{children}</section>; }
