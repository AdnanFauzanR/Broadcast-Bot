<?php

namespace App\Http\Middleware;

use App\Models\User;
use Closure;
use Illuminate\Http\Request;

class AdminAuthMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure(\Illuminate\Http\Request): (\Illuminate\Http\Response|\Illuminate\Http\RedirectResponse)  $next
     * @return \Illuminate\Http\Response|\Illuminate\Http\RedirectResponse
     */
    public function handle(Request $request, Closure $next)
    {
        $chat_id = $request->input('chat_id');

        $user = User::where('chat_id', (float)$chat_id)->first();

        if($user->role === 'admin') {
            return $next($request);
        }

        return response()->json([
        'message' => 'You are not authorized to access this page'
    ], 403);

    }
}
