<?php

namespace App\Models;

use Jenssegers\Mongodb\Eloquent\Model as Eloquent;

class User extends Eloquent
{
    protected $connection = 'mongodb';
    protected $collection = 'registered_users';

    protected $fillable = [
        '_id',
        'nama',
        'username',
        'role',
        'chat_id',
        'nik',
        'jabatan',
        'witel',
    ];
}