<?php

namespace App\Http\Controllers;

use App\Models\SecurityQuestion;
use Illuminate\Http\JsonResponse;

class SecurityQuestionController extends Controller
{
    public function index(): JsonResponse
    {
        $questions = SecurityQuestion::where('is_active', true)->orderBy('id')->get(['id', 'question']);
        return response()->json($questions);
    }
}