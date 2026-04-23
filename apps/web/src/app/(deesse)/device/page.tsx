import { redirect } from "next/navigation";
import { headers } from "next/headers";
import { deesseAuth } from "@/lib/deesse";
import DeviceVerificationPage from "@/components/device-verification-form";

export default async function DevicePage() {
  const session = await deesseAuth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login?redirectTo=/device");
  }

  return <DeviceVerificationPage />;
}
