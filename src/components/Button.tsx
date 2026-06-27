import { Link } from "react-router-dom";

type ButtonProps = {
  to?: string;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
  children: React.ReactNode;
  type?: "button" | "submit";
  disabled?: boolean;
};

const variants = {
  primary:
    "bg-teal-600 text-white hover:bg-teal-700 shadow-sm",
  secondary:
    "bg-white text-stone-900 border border-stone-200 hover:bg-stone-50",
  ghost: "text-teal-700 hover:bg-teal-50",
};

export function Button({
  to,
  onClick,
  variant = "primary",
  className = "",
  children,
  type = "button",
  disabled,
}: ButtonProps) {
  const classes = `inline-flex items-center justify-center rounded-lg px-5 py-3 text-sm font-semibold transition-colors ${variants[variant]} ${className}`;

  if (to) {
    return (
      <Link to={to} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${classes} disabled:opacity-50`}
    >
      {children}
    </button>
  );
}

export function PrimaryCta({
  to = "/signup",
  children = "Take your free mock",
  className = "",
}: {
  to?: string;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <Button to={to} className={`w-full sm:w-auto ${className}`}>
      {children}
    </Button>
  );
}
