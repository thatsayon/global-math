// components/settings/Profile.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Camera, X } from "lucide-react";
import {
  useChangePasswordMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
} from "@/store/slices/api/profileApiSlice";

const profileSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
});

const passwordSchema = z
  .object({
    currentPassword: z.string().min(6, "Current password is required"),
    newPassword: z
      .string()
      .min(6, "New password must be at least 6 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type ProfileFormData = z.infer<typeof profileSchema>;
type PasswordFormData = z.infer<typeof passwordSchema>;

export default function Profile() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const [updateProfile, { isLoading: updatingProfile }] =
    useUpdateProfileMutation();
  const [changePassword, { isLoading: changingPassword }] =
    useChangePasswordMutation();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const profileForm = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  const passwordForm = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  useEffect(() => {
    if (profile) {
      profileForm.reset({
        firstName: profile.first_name,
        lastName: profile.last_name,
      });
      setPreviewUrl(profile.profile_pic || null);
    }
  }, [profile, profileForm]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering file picker
    setSelectedFile(null);
    setPreviewUrl(profile?.profile_pic || null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  const onProfileSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile({
        first_name: data.firstName,
        last_name: data.lastName,
        profile_pic: selectedFile || undefined,
      }).unwrap();

      toast.success("Profile Updated", {
        description: "Your profile has been updated successfully.",
      });
    } catch (error) {
      const err = error as { data: { detail: string } };
      toast.error("Update Failed", {
        description: err?.data?.detail || "Something went wrong",
      });
    }
  };

  const onPasswordSubmit = async (data: PasswordFormData) => {
    try {
      await changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword,
      }).unwrap();
      toast.success("Password Changed", {
        description: "Your password has been updated successfully.",
      });
      passwordForm.reset();
    } catch (error) {
      const err = error as { data: { detail: string } };

      toast.error("Password Update Failed", {
        description: err?.data?.detail || "Invalid current password",
      });
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-6 space-y-8">
      {/* Profile Section */}
      <div className="flex flex-col items-center space-y-8">
        {/* Clickable Avatar */}
        <div className="relative group cursor-pointer" onClick={openFilePicker}>
          <Avatar className="w-32 h-32 border-4 border-white shadow-xl ring-4 ring-gray-100">
            <AvatarImage
              src={previewUrl || ""}
              alt="Profile"
              className="object-cover"
            />
            <AvatarFallback className="text-3xl font-medium bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              {profile
                ? `${profile.first_name[0]}${profile.last_name[0]}`.toUpperCase()
                : "U"}
            </AvatarFallback>
          </Avatar>

          {/* Hover Overlay */}
          <div className="absolute inset-0 rounded-full bg-black/40 bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
            <Camera className="w-8 h-8 text-white" />
          </div>

          {/* Remove button when new image selected */}
          {selectedFile && (
            <button
              onClick={removeImage}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1.5 shadow-lg hover:bg-red-600 transition"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Optional: Show filename below */}
        {selectedFile && (
          <p className="text-sm text-gray-600 flex items-center gap-2">
            <span className="font-medium">{selectedFile.name}</span>
            <span className="text-xs text-gray-400">
              • Click avatar to change
            </span>
          </p>
        )}

        {/* Name Fields */}
        <div className="w-full max-w-md space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>First Name</Label>
              <Input
                {...profileForm.register("firstName")}
                disabled={profileLoading}
                placeholder="First name"
              />
            </div>
            <div className="space-y-2">
              <Label>Last Name</Label>
              <Input
                {...profileForm.register("lastName")}
                disabled={profileLoading}
                placeholder="Last name"
              />
            </div>
          </div>

          <div className="text-center pt-4">
            <Button
              onClick={profileForm.handleSubmit(onProfileSubmit)}
              disabled={updatingProfile || profileLoading}
              size="lg"
              className="px-8"
            >
              {updatingProfile ? "Updating Profile..." : "Update Profile"}
            </Button>
          </div>
        </div>
      </div>

      {/* Password Section */}
      <div className="pt-12 border-t">
        <h2 className="text-2xl font-semibold mb-8 text-center">
          Password and Security
        </h2>
        <div className="w-full max-w-md mx-auto space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Current password</Label>
              <Input
                type="password"
                {...passwordForm.register("currentPassword")}
                placeholder="••••••••"
              />
            </div>
            <div className="space-y-2">
              <Label>New password</Label>
              <Input
                type="password"
                {...passwordForm.register("newPassword")}
                placeholder="••••••••"
              />
            </div>
            <div className="space-y-2">
              <Label>Confirm new password</Label>
              <Input
                type="password"
                {...passwordForm.register("confirmPassword")}
                placeholder="••••••••"
              />
              {passwordForm.formState.errors.confirmPassword && (
                <p className="text-sm text-red-500">
                  {passwordForm.formState.errors.confirmPassword.message}
                </p>
              )}
            </div>
          </div>

          <div className="text-center">
            <Button
              onClick={passwordForm.handleSubmit(onPasswordSubmit)}
              disabled={changingPassword}
              size="lg"
              className="px-8"
            >
              {changingPassword ? "Changing Password..." : "Change Password"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
