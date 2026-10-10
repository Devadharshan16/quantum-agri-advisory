import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center whitespace-nowrap transition-all outline-none select-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] disabled:pointer-events-none disabled:opacity-50 text-[17px] font-semibold",
  {
    variants: {
      variant: {
        default: "bg-[var(--accent)] text-white hover:opacity-90 rounded-full",
        secondary: "bg-[var(--elevated)] bg-black/5 dark:bg-white/10 text-[var(--foreground)] hover:bg-black/10 dark:hover:bg-white/20 rounded-xl",
        ghost: "hover:bg-black/5 dark:hover:bg-white/10 text-[var(--foreground)] rounded-xl",
      },
      size: {
        default: "h-[44px] px-6",
        sm: "h-9 px-4 text-[15px]",
        icon: "h-[44px] w-[44px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
