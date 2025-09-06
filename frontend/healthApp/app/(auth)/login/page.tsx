import { GalleryVerticalEnd } from "lucide-react"

import { LoginForm } from "@/components/login-form"
import blobRightBlue from "@/assets/blob-right.svg"

export default function LoginPage() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2 bg-background">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-bold text-primary">
            <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Acme Inc.
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm />
          </div>
        </div>
      </div>
      <div className="bg-[#88a5f8] relative hidden lg:block">
        
        {/* <div className="absolute right-[-300px] top-1/2 -translate-y-1/2 w-[1500px] h-[1500px] bg-[#88a5f8] rounded-full z-0 filter blur-xl" /> */}
        
      </div>
    </div>
  )
}
