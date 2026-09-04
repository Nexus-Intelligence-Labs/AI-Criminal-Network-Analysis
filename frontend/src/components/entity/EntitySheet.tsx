import { Entity } from '@/types'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { User, Building2, Car, MapPin, Phone, CreditCard, FileText } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'

interface EntitySheetProps {
  entity: Entity | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

const entityIcons = {
  person: User,
  organization: Building2,
  vehicle: Car,
  location: MapPin,
  phone: Phone,
  account: CreditCard,
  case: FileText,
  evidence: FileText,
  event: FileText,
}

export function EntitySheet({ entity, open, onOpenChange }: EntitySheetProps) {
  if (!entity) return null

  const Icon = entityIcons[entity.type]

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader>
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <SheetTitle className="text-xl">{entity.name}</SheetTitle>
              <p className="text-sm text-muted-foreground capitalize mt-1">
                {entity.type.replace('_', ' ')}
              </p>
            </div>
          </div>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Status Badges */}
          <div className="flex flex-wrap gap-2">
            {entity.isHighRisk && (
              <Badge variant="destructive">High Risk</Badge>
            )}
            <Badge variant="outline">
              Confidence: {(entity.confidence * 100).toFixed(0)}%
            </Badge>
          </div>

          {/* Identity */}
          <div>
            <h3 className="text-sm font-semibold mb-2">Identity</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted-foreground">Primary ID:</span>
                <span className="ml-2 font-mono">{entity.id}</span>
              </div>
              {entity.aliases && entity.aliases.length > 0 && (
                <div>
                  <span className="text-muted-foreground">Aliases:</span>
                  <div className="ml-2 mt-1 flex flex-wrap gap-1">
                    {entity.aliases.map((alias, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {alias}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Cases */}
          <div>
            <h3 className="text-sm font-semibold mb-2">Related Cases</h3>
            <div className="space-y-2">
              {entity.caseIds.map((caseId) => (
                <div
                  key={caseId}
                  className="p-2 rounded-md border bg-card hover:bg-accent transition-fast cursor-pointer"
                >
                  <div className="font-mono text-sm">{caseId}</div>
                </div>
              ))}
              {entity.caseIds.length === 0 && (
                <p className="text-sm text-muted-foreground">No related cases</p>
              )}
            </div>
          </div>

          <Separator />

          {/* Metadata */}
          {Object.keys(entity.metadata).length > 0 && (
            <>
              <div>
                <h3 className="text-sm font-semibold mb-2">Additional Information</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(entity.metadata).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-muted-foreground capitalize">
                        {key.replace('_', ' ')}:
                      </span>
                      <span className="ml-2">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
              <Separator />
            </>
          )}

          {/* Timeline */}
          <div>
            <h3 className="text-sm font-semibold mb-2">Timeline</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted-foreground">Created:</span>
                <span className="ml-2">{formatDateTime(entity.createdAt)}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Last Updated:</span>
                <span className="ml-2">{formatDateTime(entity.updatedAt)}</span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Actions */}
          <div className="space-y-2">
            <Button className="w-full" variant="default">
              View Full Profile
            </Button>
            <Button className="w-full" variant="outline">
              Explore Network
            </Button>
            <Button className="w-full" variant="outline">
              View Evidence
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
