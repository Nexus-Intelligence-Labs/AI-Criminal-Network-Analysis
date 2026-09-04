import * as LabelPrimitive from '@radix-ui/react-label'
import type { ComponentPropsWithoutRef } from 'react'

export function Label(props: ComponentPropsWithoutRef<typeof LabelPrimitive.Root>) { return <LabelPrimitive.Root className="label" {...props} /> }
