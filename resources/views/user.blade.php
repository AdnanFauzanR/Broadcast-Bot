@extends('layouts.app') <!-- Pastikan Anda memiliki layout yang sesuai -->

@section('content')
<div class="container">
    <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" id="admin-tab" data-toggle="tab" href="#admin" role="tab" aria-controls="admin" aria-selected="true">Admin</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="user-tab" data-toggle="tab" href="#user" role="tab" aria-controls="user" aria-selected="false">User</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="bc-tab" data-toggle="tab" href="#bc" role="tab" aria-controls="bc" aria-selected="false">BC</a>
        </li>
    </ul>
    <div class="tab-content" id="myTabContent">
        <div class="tab-pane fade show active" id="admin" role="tabpanel" aria-labelledby="admin-tab">
            <button class="btn btn-primary mt-3" data-toggle="modal" data-target="#addMemberModalAdmin">Add Member</button>
            <!-- Tabel untuk menampilkan daftar anggota admin -->
            <table class="table mt-3">
                <thead>
                    <tr>
                        <th>Nama</th>
                        <th>Pilih</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Isi dengan data anggota admin -->
                    <tr>
                        <td>Anggota 1</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <tr>
                        <td>Anggota 2</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <!-- Tambahkan lebih banyak baris sesuai dengan anggota admin -->
                </tbody>
            </table>
        </div>
        <div class="tab-pane fade" id="user" role="tabpanel" aria-labelledby="user-tab">
            <button class="btn btn-primary mt-3" data-toggle="modal" data-target="#addMemberModalUser">Add Member</button>
            <!-- Tabel untuk menampilkan daftar anggota user -->
            <table class="table mt-3">
                <thead>
                    <tr>
                        <th>Nama</th>
                        <th>Pilih</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Isi dengan data anggota user -->
                    <tr>
                        <td>Anggota 1</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <tr>
                        <td>Anggota 2</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <!-- Tambahkan lebih banyak baris sesuai dengan anggota user -->
                </tbody>
            </table>
        </div>
        <div class="tab-pane fade" id="bc" role="tabpanel" aria-labelledby="bc-tab">
            <button class="btn btn-primary mt-3" data-toggle="modal" data-target="#addMemberModalBC">Add Member</button>
            <!-- Tabel untuk menampilkan daftar anggota BC -->
            <table class="table mt-3">
                <thead>
                    <tr>
                        <th>Nama</th>
                        <th>Pilih</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Isi dengan data anggota BC -->
                    <tr>
                        <td>Anggota 1</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <tr>
                        <td>Anggota 2</td>
                        <td><input type="checkbox"></td>
                    </tr>
                    <!-- Tambahkan lebih banyak baris sesuai dengan anggota BC -->
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal untuk menambahkan anggota -->
<div class="modal fade" id="addMemberModalAdmin" tabindex="-1" role="dialog" aria-labelledby="addMemberModalAdminLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="addMemberModalAdminLabel">Add Member to Admin</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <!-- Tabel untuk memilih anggota yang akan ditambahkan ke Admin -->
                <table class="table">
                    <thead>
                        <tr>
                            <th>Nama</th>
                            <th>Pilih</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Isi dengan daftar anggota yang dapat dipilih -->
                        <tr>
                            <td>Anggota 1</td>
                            <td><input type="checkbox"></td>
                        </tr>
                        <tr>
                            <td>Anggota 2</td>
                            <td><input type="checkbox"></td>
                        </tr>
                        <!-- Tambahkan lebih banyak baris sesuai dengan anggota yang dapat dipilih -->
                    </tbody>
                </table>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary">Add</button>
            </div>
        </div>
    </div>
</div>

<!-- Buat modal serupa untuk User dan BC -->
<!-- Modal untuk menambahkan anggota ke User -->
<div class="modal fade" id="addMemberModalUser" tabindex="-1" role="dialog" aria-labelledby="addMemberModalUserLabel" aria-hidden="true">
    <!-- Modal content untuk User -->
</div>

<!-- Modal untuk menambahkan anggota ke BC -->
<div class="modal fade" id="addMemberModalBC" tabindex="-1" role="dialog" aria-labelledby="addMemberModalBCLabel" aria-hidden="true">
    <!-- Modal content untuk BC -->
</div>
@endsection
