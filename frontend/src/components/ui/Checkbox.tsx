import * as CheckboxPrimitive from '@radix-ui/react-checkbox'
import { Check } from 'lucide-react'
import { cn } from '../../lib/utils'

export function Checkbox({ className, ...props }: CheckboxPrimitive.CheckboxProps) {
  return <CheckboxPrimitive.Root className={cn('checkbox', className)} {...props}><CheckboxPrimitive.Indicator><Check size={13} strokeWidth={3} /></CheckboxPrimitive.Indicator></CheckboxPrimitive.Root>
}
