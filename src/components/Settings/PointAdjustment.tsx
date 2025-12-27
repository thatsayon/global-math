"use client";

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { useGetPointAdjustmentQuery, useUpdatePointAdjustmentMutation } from '@/schema/pointApiSlice';
import { pointAdjustmentSchema } from '@/schema/point.schema';
import { LoadingState } from '../elements/Loading';

type PointFormData = {
  classroomPoint: number;
  upvotePoint: number;
  dailyChallengePoint: number;
};

export default function PointAdjustment() {
  const { data: points, isLoading } = useGetPointAdjustmentQuery();
  const [updatePoints, { isLoading: isUpdating }] = useUpdatePointAdjustmentMutation();

  const pointForm = useForm<PointFormData>({
    resolver: zodResolver(pointAdjustmentSchema),
    defaultValues: {
      classroomPoint: 0,
      upvotePoint: 0,
      dailyChallengePoint: 0,
    },
  });

  // Populate form when data loads
  React.useEffect(() => {
    if (points) {
      pointForm.reset({
        classroomPoint: points.classroom_point,
        upvotePoint: points.upvote_point,
        dailyChallengePoint: points.daily_challenge_point,
      });
    }
  }, [points, pointForm]);

  const onSubmit = async (data: PointFormData) => {
    try {
      await updatePoints({
        classroom_point: data.classroomPoint,
        upvote_point: data.upvotePoint,
        daily_challenge_point: data.dailyChallengePoint,
      }).unwrap();

      toast.success("Points Updated", {
        description: "Point adjustments have been saved successfully.",
      });
    } catch (error) {
      toast.error("Update Failed", {
        description: "Failed to save point adjustments.",
      });
    }
  };

  const onCancel = () => {
    if (points) {
      pointForm.reset({
        classroomPoint: points.classroom_point,
        upvotePoint: points.upvote_point,
        dailyChallengePoint: points.daily_challenge_point,
      });
    }
    toast("Changes Discarded", {
      description: "All changes have been cancelled.",
    });
  };

  if (isLoading) {
    return (
      <LoadingState/>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg border p-6 space-y-6">
        <h2 className="text-2xl font-semibold">Points Adjustment</h2>

        <form onSubmit={pointForm.handleSubmit(onSubmit)} className="space-y-6">
          {/* Add point for classroom */}
          <div className="space-y-2">
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="classroomPoint">
              Add point for classroom
            </Label>
            <div className="relative">
              <Input
                id="classroomPoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register("classroomPoint", { valueAsNumber: true })}
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
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="upvotePoint">
              Add point for Upvote
            </Label>
            <div className="relative">
              <Input
                id="upvotePoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register("upvotePoint", { valueAsNumber: true })}
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
            <Label className='text-gray-500 text-base lg:text-lg font-medium' htmlFor="dailyChallengePoint">
              Add point for Daily challenge
            </Label>
            <div className="relative">
              <Input
                id="dailyChallengePoint"
                type="number"
                placeholder="--- Point"
                {...pointForm.register("dailyChallengePoint", { valueAsNumber: true })}
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

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
            <Button
              type="submit"
              disabled={isUpdating}
              className="w-full sm:w-auto px-8"
            >
              {isUpdating ? "Saving..." : "Save"}
            </Button>
            <Button
              type="button"
              onClick={onCancel}
              variant="outline"
              className="w-full sm:w-auto px-8 border-red-500 text-red-500 hover:bg-red-50"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}