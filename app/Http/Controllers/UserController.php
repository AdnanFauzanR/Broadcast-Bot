<?php

namespace App\Http\Controllers;

use Exception;
use Illuminate\Http\Request;
use App\Models\User;
use Jenssegers\Mongodb\Eloquent\Model as Eloquent;

class UserController extends Eloquent
{
    public function getAllUsernames() {
        try {
            $users = User::all();
        $usernames = $users->pluck('username')->toArray();

        return response()->json([
            'usernames' => $usernames,
        ], 200);
        } catch(Exception $e) {
            return response()->json([
                'error' => 'An error occured while fetching usernames'
            ], 500);
        }

    }

    public function changeRoles(Request $request) {
        $roleMappings = $request->input('roles');

        if (empty($roleMappings)) {
            return response()->json(['error' => 'No role mappings provided'], 400);
        }

        foreach ($roleMappings as $mapping) {
            $userId = $mapping['user_id'];
            $newRole = $mapping['new_role'];

            if (!in_array($newRole, ['admin', 'broadcaster', 'member'])) {
                return response()->json(['error' => 'Invalid Role'], 400);
            }

            try {
                $user = User::find($userId);

                if (!$user) {
                    return response()->json(['error' => 'User not found'], 404);
                }

                $user->role = $newRole;
                $user->save();
            } catch (Exception $e) {
                return response()->json([
                    'error' => 'An error occurred while updating the role'
                ], 500);
            }
        }

        return response()->json([
            'message' => 'Roles updated successfully'
        ], 200);
    }


    public function index($role) {
        if (!in_array($role, ['admin', 'broadcaster', 'member'])) {
            return response()->json([
                'error' => 'Invalid role'
            ], 400);
        }

        try {
            $users = User::where('role', $role)->get();
            return response()->json($users, 200);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'An error occured while fetching users'
            ], 500);
        }
    }

    public function deleteUser($id) {
        try {
            $user = User::find($id);

            if(!$user) {
                return response()->json([
                    'error' => 'User not found'
                ], 404);
            }

            $user->delete();

            return response()->json([
                'message' => 'User deleted successfully'
            ], 200);
        } catch(Exception $e) {
            return response()->json([
                'error' => 'An error occured while deleting the user'
            ], 500);
        }
    }
}
