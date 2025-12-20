"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Logo from "../elements/Logo";
import { Mail, Eye, EyeOff, Loader } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

// react-hook-form + zod
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useLoginMutation } from "@/store/slices/api/ApiSlice";
import { setCookie } from "@/hooks/cookie";
import { toast } from "sonner";

// ✅ Validation Schema
const loginSchema = z.object({
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(4, "Password must be at least 4 characters"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);

  // api endpoint

  const [login, {isLoading}] = useLoginMutation();

  // ✅ Setup form
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  // ✅ Submit handler
 const onSubmit = async (data: LoginFormValues) => {
  try {
    const response = await login(data).unwrap();

    if (response.access && response.refresh) {
      // Access: 5 minutes, Refresh: 30 days
      setCookie('access', response.access, 1 / (24 * 60)); // 5 minutes in days
      setCookie('refresh', response.refresh, 30);

      toast.success('Welcome back!');
      router.push('/dashboard');
    }
  } catch (err: any) {
    toast.error(err?.data?.detail || 'Invalid credentials');
  }
};

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <div className="flex justify-center mb-7">
            <Logo />
          </div>
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>
            Login with your Admin Email and Password
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid gap-6">
              <div className="grid gap-6">
                {/* Email */}
                <div className="grid gap-3">
                  <Label htmlFor="email">Email Address</Label>
                  <div className="relative">
                    <Input
                      id="email"
                      type="email"
                      placeholder="m@example.com"
                      className="h-10"
                      {...register("email")}
                    />
                    <Mail className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                  </div>
                  {errors.email && (
                    <p className="text-sm text-red-500">
                      {errors.email.message}
                    </p>
                  )}
                </div>

                {/* Password */}
                <div className="grid gap-3">
                  <div className="flex items-center">
                    <Label htmlFor="password">Password</Label>
                  </div>
                  <div className="relative">
                    <Input
                      id="password"
                      placeholder="your password"
                      type={showPassword ? "text" : "password"}
                      className="h-10"
                      {...register("password")}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="text-sm text-red-500">
                      {errors.password.message}
                    </p>
                  )}
                </div>

                <Button
                  size={"lg"}
                  disabled={isLoading}
                  type="submit"
                  className="w-full bg-[#3B82F6] min-h-12"
                >
                  {isLoading ? <span className="animate-spin"><Loader/></span> : "Login"}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
