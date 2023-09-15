<?php

namespace App\Http\Controllers;

use Exception;
use Illuminate\Http\Request;
use App\Models\User;
use Jenssegers\Mongodb\Eloquent\Model as Eloquent;

class UserController extends Eloquent
{
    
    public function changeRole($id, Request $request) {
        $newRole = $request->input('new_role');

        if(!in_array($newRole, ['admin', 'broadcaster', 'member'])) {
            return response()->json(['error' => 'Invalid Role'], 400);
        }

        try {
            $user = User::find($id);

            if(!$user) {
                return response()->json(['error' => 'User not found'], 404);
            }

            $user->role = $newRole;
            $user->save();

            return response()->json([
                'message' => 'Role updated successfully'
            ], 200);
        } catch (Exception $e){
            return response()->json([
                'error' => 'An error occured while updating the role'
            ], 500);
        }
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
