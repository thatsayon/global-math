"use client"
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

// Profile form schema
const profileSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
});

// Password form schema
const passwordSchema = z.object({
  currentPassword: z.string().min(6, 'Password must be at least 6 characters'),
  newPassword: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Password must be at least 6 characters'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ProfileFormData = z.infer<typeof profileSchema>;
type PasswordFormData = z.infer<typeof passwordSchema>;

export default function Profile() {

  // Profile form
  const profileForm = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      fullName: 'Bradley Jones',
    },
  });

  // Password form
  const passwordForm = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onProfileSubmit = (data: ProfileFormData) => {
    console.log('Profile Update:', data);
    toast("Profile Updated",{
      description: "Your profile has been updated successfully.",
    });
  };

  const onPasswordSubmit = (data: PasswordFormData) => {
    console.log('Password Updated:', data);
    toast("Profile Updated",{
      description: "Your password has been changed successfully",
    });
    passwordForm.reset();
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-6 space-y-8">
      {/* Profile Section */}
      <div className="flex flex-col items-center space-y-6">
        <Avatar className="w-32 h-32">
          <AvatarImage src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop" alt="Bradley Jones" />
          <AvatarFallback>BJ</AvatarFallback>
        </Avatar>

        <div className="w-full max-w-md space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">Full name</Label>
            <Input
              id="fullName"
              {...profileForm.register('fullName')}
              className="w-full"
            />
            {profileForm.formState.errors.fullName && (
              <p className="text-sm text-red-500">
                {profileForm.formState.errors.fullName.message}
              </p>
            )}
          </div>

          <div className='text-center'>
            <Button 
            onClick={profileForm.handleSubmit(onProfileSubmit)} 
            className="w-full sm:w-auto"
          >
            Update Profile
          </Button>
          </div>
        </div>
      </div>

      {/* Password and Security Section */}
      <div className="pt-6">
        <h2 className="text-xl font-semibold mb-6 text-center">Password and security</h2>
        
        <div className="w-full max-w-md mx-auto space-y-4">
          <div className="space-y-2">
            <Label htmlFor="currentPassword">Current password</Label>
            <Input
              id="currentPassword"
              type="password"
              placeholder="John123#$8"
              {...passwordForm.register('currentPassword')}
              className="w-full"
            />
            {passwordForm.formState.errors.currentPassword && (
              <p className="text-sm text-red-500">
                {passwordForm.formState.errors.currentPassword.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="newPassword">New password</Label>
            <Input
              id="newPassword"
              type="password"
              placeholder="John123#$8"
              {...passwordForm.register('newPassword')}
              className="w-full"
            />
            {passwordForm.formState.errors.newPassword && (
              <p className="text-sm text-red-500">
                {passwordForm.formState.errors.newPassword.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm password</Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="John123#$8"
              {...passwordForm.register('confirmPassword')}
              className="w-full"
            />
            {passwordForm.formState.errors.confirmPassword && (
              <p className="text-sm text-red-500">
                {passwordForm.formState.errors.confirmPassword.message}
              </p>
            )}
          </div>

          <div className='text-center'>
            <Button 
            onClick={passwordForm.handleSubmit(onPasswordSubmit)} 
            className="w-full sm:w-auto"
          >
            Update password
          </Button>
          </div>
        </div>
      </div>
    </div>
  );
}