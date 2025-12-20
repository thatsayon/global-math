"use client"
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Pencil } from 'lucide-react';
import { toast } from 'sonner';

// Point adjustment form schema
const pointSchema = z.object({
  classroomPoint: z.string().min(1, 'Classroom point is required'),
  upvotePoint: z.string().min(1, 'Upvote point is required'),
  dailyChallengePoint: z.string().min(1,   'Daily challenge point is required'),
});

type PointFormData = z.infer<typeof pointSchema>;

export default function PointAdjustment() {

  const pointForm = useForm<PointFormData>({
    resolver: zodResolver(pointSchema),
    defaultValues: {
      classroomPoint: '',
      upvotePoint: '',
      dailyChallengePoint: '',
    },
  });

  const onSubmit = (data: PointFormData) => {
    console.log('Point Adjustment Data:', data);
    toast("Points Updated",{
      description: "Point adjustments have been saved successfully.",
    });
  };

  const onCancel = () => {
    pointForm.reset();
    toast.error("Changes Discarded",{
      description: "All changes have been cancelled.",
    });
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg border p-6 space-y-6">
        <h2 className="text-2xl font-semibold">Points Adjustment</h2>

        <div className="space-y-6">
          {/* Add point for classroom */}
          <div className="space-y-2">
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="classroomPoint">Add point for classroom</Label>
            <div className="relative">
              <Input
                id="classroomPoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register('classroomPoint')}
                className="w-full pr-10 h-10 lg:h-12"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {pointForm.formState.errors.classroomPoint && (
              <p className="text-sm text-red-500">
                {pointForm.formState.errors.classroomPoint.message}
              </p>
            )}
          </div>

          {/* Add point for Upvote */}
          <div className="space-y-2">
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="upvotePoint">Add point for Upvote</Label>
            <div className="relative">
              <Input
                id="upvotePoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register('upvotePoint')}
                className="w-full pr-10 h-10 lg:h-12"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {pointForm.formState.errors.upvotePoint && (
              <p className="text-sm text-red-500">
                {pointForm.formState.errors.upvotePoint.message}
              </p>
            )}
          </div>

          {/* Add point for Daily challenge */}
          <div className="space-y-2">
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="dailyChallengePoint">Add point for Daily challenge</Label>
            <div className="relative">
              <Input
                id="dailyChallengePoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register('dailyChallengePoint')}
                className="w-full pr-10 h-10 lg:h-12"
              />
              <Pencil className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {pointForm.formState.errors.dailyChallengePoint && (
              <p className="text-sm text-red-500">
                {pointForm.formState.errors.dailyChallengePoint.message}
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
          <Button 
            onClick={pointForm.handleSubmit(onSubmit)}
            className="w-full sm:w-auto px-8"
          >
            Save
          </Button>
          <Button 
            onClick={onCancel}
            variant="outline"
            className="w-full sm:w-auto px-8 border-red-500 text-red-500 hover:bg-red-50"
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}