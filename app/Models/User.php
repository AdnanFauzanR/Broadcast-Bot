<?php

namespace App\Models;

use Jenssegers\Mongodb\Eloquent\Model as Eloquent;

class User extends Eloquent
{
    protected $connection = 'mongodb';
    protected $collection = 'registered_users';

    protected $fillable = [
        '_id', 'name', 'username', 'role', 'chat_id', 'nik', 'jabatan', 'witel', 'wilayah'
    ];
}

