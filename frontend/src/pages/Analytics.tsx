import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Network, Users, FolderOpen, AlertTriangle } from 'lucide-react'

const entityData = [
  { type: 'Person', count: 5 },
  { type: 'Organization', count: 1 },
  { type: 'Vehicle', count: 1 },
  { type: 'Location', count: 1 },
  { type: 'Phone', count: 1 },
  { type: 'Account', count: 1 },
]

const relationshipData = [
  { type: 'owns', value: 2 },
  { type: 'works_with', value: 1 },
  { type: 'knows', value: 3 },
  { type: 'transacted_with', value: 2 },
  { type: 'contacted', value: 1 },
  { type: 'located_at', value: 1 },
  { type: 'associated_with', value: 1 },
]

const caseActivityData = [
  { date: '01/08', cases: 1 },
  { date: '01/09', cases: 2 },
  { date: '01/10', cases: 2 },
  { date: '01/11', cases: 3 },
  { date: '01/12', cases: 4 },
  { date: '01/13', cases: 4 },
  { date: '01/14', cases: 4 },
]

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#06b6d4', '#ec4899']

export function Analytics() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Network intelligence and investigative metrics
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <div className="grid gap-6">
          {/* Network Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Total Entities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">10</div>
                <p className="text-xs text-muted-foreground">Across all types</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Network className="h-4 w-4" />
                  Relationships
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">11</div>
                <p className="text-xs text-muted-foreground">Connections</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <FolderOpen className="h-4 w-4" />
                  Active Cases
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4</div>
                <p className="text-xs text-muted-foreground">In progress</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  Signals
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">6</div>
                <p className="text-xs text-muted-foreground">Analytical signals</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Entity Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={entityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Relationship Types</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={relationshipData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => String(entry.name)}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {relationshipData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Case Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={caseActivityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="cases" stroke="#3b82f6" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
