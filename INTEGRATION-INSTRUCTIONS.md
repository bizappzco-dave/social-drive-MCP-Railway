/**
 * MCP Template Matching Integration for SocialDrive Upload
 * 
 * Add this to pro-page.tsx to enable client-side image analysis
 */

// 1. Add new state variables (after line 30)
const [templateMatch, setTemplateMatch] = useState<any>(null)
const [analyzing, setAnalyzing] = useState(false)
const [mcpError, setMcpError] = useState<string | null>(null)

// 2. Add this function after handleFileSelect (around line 78)
async function analyzeImagesWithMCP() {
  if (images.length === 0) return
  
  setAnalyzing(true)
  setMcpError(null)
  
  try {
    // Convert first image to base64
    const file = images[0]
    const base64 = await fileToBase64(file)
    
    // Call MCP server
    const response = await fetch('http://localhost:8765/template/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: base64,
        industry: 'barber'  // Or get from client profile
      })
    })
    
    if (!response.ok) {
      throw new Error('MCP server unavailable')
    }
    
    const result = await response.json()
    
    if (result.success) {
      setTemplateMatch(JSON.parse(result.response))
    } else {
      setMcpError(result.error || 'Analysis failed')
    }
  } catch (err: any) {
    console.error('MCP analysis failed:', err)
    setMcpError('Could not connect to MCP server. Continuing without template...')
  } finally {
    setAnalyzing(false)
  }
}

// 3. Add this helper function
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = error => reject(error)
  })
}

// 4. Add useEffect to trigger analysis when images change (after line 39)
useEffect(() => {
  if (images.length > 0) {
    analyzeImagesWithMCP()
  }
}, [images])

// 5. Add template preview UI in the form (after image previews, before submit button)
{analyzing && (
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div className="flex items-center gap-2">
      <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
      <p className="text-sm text-blue-800 font-medium">Analyzing images...</p>
    </div>
  </div>
)}

{templateMatch && (
  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
    <div className="flex items-start gap-2 mb-3">
      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
      <div>
        <h3 className="text-sm font-semibold text-green-900">Template Matched</h3>
        <p className="text-xs text-green-700 mt-1">
          Scene: <span className="font-medium">{templateMatch.scene_type}</span>
        </p>
      </div>
    </div>
    
    <div className="space-y-2">
      <p className="text-xs text-green-800 font-medium">Key elements:</p>
      <div className="flex flex-wrap gap-1">
        {templateMatch.key_elements.map((element: string, i: number) => (
          <span key={i} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            {element}
          </span>
        ))}
      </div>
    </div>
    
    {templateMatch.suggested_templates && templateMatch.suggested_templates.length > 0 && (
      <div className="mt-3 pt-3 border-t border-green-200">
        <p className="text-xs text-green-800 font-medium mb-2">Suggested caption style:</p>
        <p className="text-xs text-green-900 italic">
          "{templateMatch.suggested_templates[0]}"
        </p>
      </div>
    )}
  </div>
)}

{mcpError && (
  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
    <p className="text-xs text-yellow-800">{mcpError}</p>
  </div>
)}

// 6. Pass template data to submit handler
async function handleSubmit(e: React.FormEvent) {
  e.preventDefault()
  
  // ... existing validation ...
  
  try {
    // Upload images
    const uploadedImages = await Promise.all(...)
    
    // Create submission WITH template metadata
    const submitResponse = await fetch(`/api/submissions/upload/${token}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uploadType,
        platforms,
        briefText: brief,
        hasVoiceNote: !!voiceNote,
        images: uploadedImages,
        templateMatch: templateMatch,  // ← Add this
      }),
    })
    
    // ... rest of submit logic ...
  }
}
