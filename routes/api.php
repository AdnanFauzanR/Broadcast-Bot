<?php

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

Route::get('/test', function(Request $request) {
    $chat_id = $request->input('chat_id');
    $user = User::where('chat_id', (float)$chat_id)->first();
    return response()->json($user);
});

Route::get('/user/{role}', [UserController::class, 'index']);
Route::get('/username/{role}', [UserController::class, 'getAllUsernames']);
Route::post('/changeRole/{role}', [UserController::class, 'changeRoles']);
Route::delete('/user/{id}', [UserController::class, 'deleteUser']);
