"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Loader2, CheckCircle, XCircle, Shield, Monitor, Clock, MapPin } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DeviceInfo {
  userCode: string
  status: "pending" | "approved" | "denied" | "expired"
  clientId?: string
  scope?: string
  expiresAt?: Date
}

async function verifyDeviceCode(userCode: string): Promise<{ userCode: string; status: string } | null> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"
    const response = await fetch(`${baseUrl}/api/auth/device?user_code=${encodeURIComponent(userCode)}`)
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.error_description || data.error || "Invalid verification code")
    }
    return response.json()
  } catch (err) {
    if (err instanceof Error) throw err
    throw new Error("Failed to verify device code")
  }
}

async function approveDevice(userCode: string): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"
  const response = await fetch(`${baseUrl}/api/auth/device/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userCode }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error_description || data.error || "Failed to approve device")
  }
}

async function denyDevice(userCode: string): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"
  const response = await fetch(`${baseUrl}/api/auth/device/deny`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userCode }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error_description || data.error || "Failed to deny device")
  }
}

function DeviceVerificationForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [userCode, setUserCode] = useState("")
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Get user_code from URL if present
  const urlUserCode = searchParams.get("user_code")

  useEffect(() => {
    if (urlUserCode) {
      setUserCode(urlUserCode)
      verifyDevice(urlUserCode)
    }
  }, [urlUserCode])

  async function verifyDevice(code: string) {
    setIsVerifying(true)
    setError(null)

    try {
      const response = await verifyDeviceCode(code)

      if (!response) {
        setError("Invalid verification code")
        setDeviceInfo(null)
        return
      }

      setDeviceInfo({
        userCode: response.userCode || response.user_code,
        status: response.status as DeviceInfo["status"],
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify device code")
      setDeviceInfo(null)
    } finally {
      setIsVerifying(false)
    }
  }

  async function handleVerify(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!userCode.trim()) return
    verifyDevice(userCode.trim())
  }

  async function handleApprove() {
    if (!deviceInfo) return
    setIsLoading(true)
    setError(null)

    try {
      await approveDevice(deviceInfo.userCode)
      toast.success("Device approved successfully")
      router.push("/home")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to approve device")
      setError(err instanceof Error ? err.message : "Failed to approve device")
    } finally {
      setIsLoading(false)
    }
  }

  async function handleDeny() {
    if (!deviceInfo) return
    setIsLoading(true)
    setError(null)

    try {
      await denyDevice(deviceInfo.userCode)
      toast.success("Device denied")
      router.push("/home")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to deny device")
      setError(err instanceof Error ? err.message : "Failed to deny device")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-1 items-center justify-center py-12">
      <div className="mx-auto w-full max-w-md space-y-6">
        <div className="space-y-2 text-center">
          <div className="flex justify-center">
            <div className="rounded-full bg-primary/10 p-3">
              <Shield className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Device Authorization</h1>
          <p className="text-sm text-muted-foreground">
            Verify and authorize a device to access your Fresh account
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {!deviceInfo ? (
          <form className="space-y-4" onSubmit={handleVerify}>
            <div className="space-y-2">
              <Label htmlFor="userCode">Verification Code</Label>
              <Input
                id="userCode"
                value={userCode}
                onChange={(e) => setUserCode(e.target.value.toUpperCase())}
                placeholder="XXXX-XXXX"
                className="text-center text-lg tracking-widest font-mono"
                maxLength={9}
                required
                disabled={isVerifying}
              />
              <p className="text-xs text-muted-foreground text-center">
                Enter the code displayed on your terminal
              </p>
            </div>
            <Button className="w-full" type="submit" disabled={isVerifying || !userCode.trim()}>
              {isVerifying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Verifying...
                </>
              ) : (
                "Verify Code"
              )}
            </Button>
          </form>
        ) : (
          <div className="space-y-6">
            {/* Status Badge */}
            <div className="flex justify-center">
              {deviceInfo.status === "pending" && (
                <span className="inline-flex items-center rounded-full bg-yellow-500/10 px-3 py-1 text-sm font-medium text-yellow-600 dark:text-yellow-400">
                  <Clock className="mr-1 h-4 w-4" />
                  Pending Authorization
                </span>
              )}
              {deviceInfo.status === "approved" && (
                <span className="inline-flex items-center rounded-full bg-green-500/10 px-3 py-1 text-sm font-medium text-green-600 dark:text-green-400">
                  <CheckCircle className="mr-1 h-4 w-4" />
                  Approved
                </span>
              )}
              {deviceInfo.status === "denied" && (
                <span className="inline-flex items-center rounded-full bg-red-500/10 px-3 py-1 text-sm font-medium text-red-600 dark:text-red-400">
                  <XCircle className="mr-1 h-4 w-4" />
                  Denied
                </span>
              )}
              {deviceInfo.status === "expired" && (
                <span className="inline-flex items-center rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
                  <Clock className="mr-1 h-4 w-4" />
                  Expired
                </span>
              )}
            </div>

            {/* Device Info Card */}
            <div className="rounded-lg border bg-card p-4 space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Monitor className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Client:</span>
                  <span className="font-medium">{deviceInfo.clientId || "Fresh CLI"}</span>
                </div>

                <div className="flex items-center gap-3 text-sm">
                  <Shield className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Code:</span>
                  <span className="font-mono font-medium tracking-wider">{deviceInfo.userCode}</span>
                </div>

                {deviceInfo.scope && (
                  <div className="flex items-center gap-3 text-sm">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Scope:</span>
                    <span className="font-medium">{deviceInfo.scope}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Anti-phishing notice */}
            <p className="text-xs text-muted-foreground text-center">
              Make sure the code above matches what you see in your terminal.
              If the codes don&apos;t match, do not approve this request.
            </p>

            {/* Action Buttons */}
            {deviceInfo.status === "pending" && (
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handleDeny}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <XCircle className="mr-2 h-4 w-4" />
                  )}
                  Deny
                </Button>
                <Button
                  variant="default"
                  className="flex-1"
                  onClick={handleApprove}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <CheckCircle className="mr-2 h-4 w-4" />
                  )}
                  Approve
                </Button>
              </div>
            )}

            {deviceInfo.status !== "pending" && (
              <Button variant="outline" className="w-full" onClick={() => router.push("/home")}>
                Return Home
              </Button>
            )}
          </div>
        )}

        <p className="text-center text-xs text-muted-foreground">
          Authorizing a device allows the Fresh CLI to access your account.
        </p>
      </div>
    </div>
  )
}

export default function DeviceVerificationPage() {
  return (
    <Suspense fallback={<div className="flex flex-1 items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin" /></div>}>
      <DeviceVerificationForm />
    </Suspense>
  )
}
