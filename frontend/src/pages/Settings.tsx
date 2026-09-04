import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Palette, Layout, Network as NetworkIcon, User } from 'lucide-react'
import { useTheme } from '@/context/useTheme'

export function Settings() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your workspace preferences
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <Tabs defaultValue="appearance" className="space-y-4">
          <TabsList>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="workspace">Workspace</TabsTrigger>
            <TabsTrigger value="graph">Graph</TabsTrigger>
            <TabsTrigger value="account">Account</TabsTrigger>
          </TabsList>

          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  <CardTitle>Appearance</CardTitle>
                </div>
                <CardDescription>
                  Customize the visual appearance of the application
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-base mb-4 block">Theme</Label>
                  <div className="grid grid-cols-2 gap-4">
                    <Button
                      variant={theme === 'dark' ? 'default' : 'outline'}
                      className="flex flex-col items-center gap-2 h-auto py-4"
                      onClick={() => theme === 'light' && toggleTheme()}
                    >
                      <div className="w-12 h-12 rounded-md bg-slate-950 border-2 border-current" />
                      Dark
                    </Button>
                    <Button
                      variant={theme === 'light' ? 'default' : 'outline'}
                      className="flex flex-col items-center gap-2 h-auto py-4"
                      onClick={() => theme === 'dark' && toggleTheme()}
                    >
                      <div className="w-12 h-12 rounded-md bg-white border-2 border-current" />
                      Light
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="workspace">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Layout className="h-5 w-5" />
                  <CardTitle>Workspace</CardTitle>
                </div>
                <CardDescription>
                  Configure your workspace layout and behavior
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Default Graph Layout</Label>
                  <p className="text-sm text-muted-foreground mb-2">
                    Choose the default layout algorithm for graph visualization
                  </p>
                  <div className="text-sm">Current: COSE (Force-Directed)</div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="graph">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <NetworkIcon className="h-5 w-5" />
                  <CardTitle>Graph Preferences</CardTitle>
                </div>
                <CardDescription>
                  Configure graph visualization behavior
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Graph Settings</Label>
                  <p className="text-sm text-muted-foreground">
                    Advanced graph settings will be available in future updates
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="account">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  <CardTitle>Account</CardTitle>
                </div>
                <CardDescription>
                  Account and profile settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg border p-4 bg-muted/50">
                  <p className="text-sm text-muted-foreground">
                    Authentication will be integrated with the backend system.
                    User account management is not yet available in this demo version.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
