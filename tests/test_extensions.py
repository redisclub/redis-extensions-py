# -*- coding: utf-8 -*-

import json

import pytest


class TestRedisExtensionsCommands(object):

    # Configs Section

    def test_timezone(self, r):
        assert not r.timezone

    def test_timezone2(self, r2):
        assert r2.timezone == 'Asia/Shanghai'

    def test_timezone3(self, r3):
        assert r3.timezone == 'Asia/Shanghai'

    # Keys Section

    def test_delete_keys(self, r):
        # Keys
        r['a:x'] = 'foo'
        r['a:y'] = 'bar'
        result = r.delete_keys('a:*')
        assert result == 2
        assert not r.exists('a:x')
        assert not r.exists('a:y')
        # Scan_iter
        r['a:x'] = 'foo'
        r['a:y'] = 'bar'
        result = r.delete_keys('a:*', iter=True)
        assert result == 2
        assert not r.exists('a:x')
        assert not r.exists('a:y')
        # Keys Count
        r['a:x'] = 'foo'
        r['a:y'] = 'bar'
        result = r.delete_keys('a:*', count=1)
        assert result == 2
        assert not r.exists('a:x')
        assert not r.exists('a:y')
        # Scan_iter Count
        r['a:x'] = 'foo'
        r['a:y'] = 'bar'
        result = r.delete_keys('a:*', iter=True, count=1)
        assert result == 2
        assert not r.exists('a:x')
        assert not r.exists('a:y')

    def test_incr_limit(self, r):
        assert r.incr_limit('a') == 1
        assert r.incr_limit('a', 5) == 6
        assert r.incr_limit('a', 10, 10) == 10
        assert r.incr_limit('a', 10, 10, 12) == 12

    def test_decr_limit(self, r):
        assert r.decr_limit('a') == -1
        assert r.decr_limit('a', 5) == -6
        assert r.decr_limit('a', 10, -10) == -10
        assert r.decr_limit('a', 10, -10, -12) == -12

    def test_incr_cmp(self, r):
        amount, gt = r.incr_cmp('a')
        assert amount == 1
        assert gt
        amount, gt = r.incr_cmp('a', cmp='>')
        assert amount == 2
        assert gt
        amount, ge = r.incr_cmp('a', cmp='>=', limit=3)
        assert amount == 3
        assert ge
        amount, eq = r.incr_cmp('a', cmp='==', limit=4)
        assert amount == 4
        assert eq
        with pytest.raises(ValueError):
            r.incr_cmp('a', cmp='+')

    def test_incr_gt(self, r):
        amount, gt = r.incr_gt('a')
        assert amount == 1
        assert gt
        amount, gt = r.incr_gt('a', 1, limit=10)
        assert amount == 2
        assert not gt

    def test_incr_ge(self, r):
        amount, ge = r.incr_ge('a', limit=1)
        assert amount == 1
        assert ge
        amount, ge = r.incr_ge('a', 1, limit=10)
        assert amount == 2
        assert not ge

    def test_incr_eq(self, r):
        amount, eq = r.incr_eq('a', limit=1)
        assert amount == 1
        assert eq
        amount, eq = r.incr_eq('a', 1, limit=10)
        assert amount == 2
        assert not eq

    def test_decr_cmp(self, r):
        amount, lt = r.decr_cmp('a')
        assert amount == -1
        assert lt
        amount, lt = r.decr_cmp('a', cmp='<')
        assert amount == -2
        assert lt
        amount, le = r.decr_cmp('a', cmp='<=', limit=-3)
        assert amount == -3
        assert le
        amount, eq = r.decr_cmp('a', cmp='==', limit=-4)
        assert amount == -4
        assert eq
        with pytest.raises(ValueError):
            r.decr_cmp('a', cmp='+')

    def test_decr_lt(self, r):
        amount, lt = r.decr_lt('a')
        assert amount == -1
        assert lt
        amount, lt = r.decr_lt('a', 1, limit=-10)
        assert amount == -2
        assert not lt

    def test_decr_le(self, r):
        amount, le = r.decr_le('a', limit=-1)
        assert amount == -1
        assert le
        amount, le = r.decr_le('a', 1, limit=-10)
        assert amount == -2
        assert not le

    def test_decr_eq(self, r):
        amount, eq = r.decr_eq('a', limit=-1)
        assert amount == -1
        assert eq
        amount, eq = r.decr_eq('a', 1, limit=-10)
        assert amount == -2
        assert not eq

    # Strings Section

    def test_get_delete(self, r):
        result = r.get_delete('a')
        assert isinstance(result, list)
        r['a'] = 'foo'
        result = r.get_delete('a')
        assert result[0] == 'foo'

    def test_get_rename(self, r):
        result = r.get_rename('a')
        assert isinstance(result, list)
        r['a'] = 'foo'
        result = r.get_rename('a')
        assert result[0] == 'foo'
        assert r.exists('a_del')

    def test_getsetex(self, r):
        assert r.getsetex('a', 60, 'foo') is None
        assert 0 < r.ttl('a') <= 60
        assert r.getsetex('a', 60, 'bar') == 'foo'
        assert 0 < r.ttl('a') <= 60

    def test_get_or_set(self, r):
        result = r.get_or_set('a', 'foo')
        assert isinstance(result, list)
        assert result[0] == 'foo'

    def test_get_or_setex(self, r):
        result = r.get_or_setex('a', 60, 'foo')
        assert isinstance(result, list)
        assert result[0] == 'foo'
        assert 0 < r.ttl('a') <= 60

    # Lists Section

    def test_lpush_nx(self, r):
        r.lpush('a', 'foo')
        r.lpush('a', 'bar')
        r.lpush_nx('a', 'foo', force=False)
        result = r.lrange('a', 0, -1)
        assert result == ['bar', 'foo']
        r.lpush_nx('a', 'foo', force=True)
        result = r.lrange('a', 0, -1)
        assert result == ['foo', 'bar']

    def test_rpush_nx(self, r):
        r.rpush('a', 'foo')
        r.rpush('a', 'bar')
        r.rpush_nx('a', 'foo', force=False)
        result = r.lrange('a', 0, -1)
        assert result == ['foo', 'bar']
        r.rpush_nx('a', 'foo', force=True)
        result = r.lrange('a', 0, -1)
        assert result == ['bar', 'foo']

    def test_multi_lpop(self, r):
        r.rpush('a', *range(10))
        result = r.multi_lpop('a', 3)
        assert isinstance(result, list)
        assert len(result[0]) == 3
        assert result[-1] == 7

        result = r.multi_lpop('a')
        assert isinstance(result, list)
        assert len(result[0]) == 1
        assert result[-1] == 6

        with pytest.raises(ValueError):
            r.multi_lpop('a', -1)

    def test_multi_rpop(self, r):
        r.rpush('a', *range(10))
        result = r.multi_rpop('a', 3)
        assert isinstance(result, list)
        assert len(result[0]) == 3
        assert result[-1] == 7

        result = r.multi_rpop('a')
        assert isinstance(result, list)
        assert len(result[0]) == 1
        assert result[-1] == 6

        with pytest.raises(ValueError):
            r.multi_rpop('a', -1)

    def test_multi_lpop_delete(self, r):
        r.rpush('a', *range(10))
        result = r.multi_lpop_delete('a', 3)
        assert isinstance(result, list)
        assert len(result[0]) == 3
        assert result[-1]
        assert not r.exists('a')

        r.rpush('a', *range(10))
        result = r.multi_lpop_delete('a')
        assert isinstance(result, list)
        assert len(result[0]) == 1
        assert result[-1]
        assert not r.exists('a')

        with pytest.raises(ValueError):
            r.multi_lpop('a', -1)

    def test_multi_rpop_delete(self, r):
        r.rpush('a', *range(10))
        result = r.multi_rpop_delete('a', 3)
        assert isinstance(result, list)
        assert len(result[0]) == 3
        assert result[-1]
        assert not r.exists('a')

        r.rpush('a', *range(10))
        result = r.multi_rpop_delete('a')
        assert isinstance(result, list)
        assert len(result[0]) == 1
        assert result[-1]
        assert not r.exists('a')

        with pytest.raises(ValueError):
            r.multi_rpop('a', -1)

    def test_trim_lpush(self, r):
        r.trim_lpush('a', 3, *range(10))
        assert r.llen('a') == 3

    def test_trim_rpush(self, r):
        r.trim_rpush('a', 3, *range(10))
        assert r.llen('a') == 3

    def test_delete_lpush(self, r):
        result = r.delete_lpush('a', *range(10))
        assert result[0] == 10
        assert not result[1]
        result = r.delete_lpush('a', *range(10))
        assert result[0] == 10
        assert result[1]

    def test_delete_rpush(self, r):
        result = r.delete_rpush('a', *range(10))
        assert result[0] == 10
        assert not result[1]
        result = r.delete_rpush('a', *range(10))
        assert result[0] == 10
        assert result[1]

    def test_lpush_ex(self, r):
        pass

    def test_lrange_ex(self, r):
        pass

    def test_sorted_pop(self, r):
        r.rpush('a', *range(10))
        assert r.sorted_pop('a', 3) == '6'

        item1 = json.dumps({'a': 1, 'b': 'a'})
        item2 = json.dumps({'a': 2, 'b': 'b'})
        r.rpush('b', *[item1, item2])

        # func = lambda x: json.loads(x).get('a', 0)
        def func(x):
            json.loads(x).get('a', 0)

        assert r.sorted_pop('b', 1, sorted_func=func, reverse=False) == item2

        with pytest.raises(IndexError):
            r.sorted_pop('b', 1, sorted_func=func, reverse=False)

    # Sets Section

    def test_delete_sadd(self, r):
        result = r.delete_sadd('a', *range(10))
        assert result[0] == 10
        assert not result[1]
        result = r.delete_sadd('a', *range(10))
        assert result[0] == 10
        assert result[1]

    # ZSorts(Sorted Sets) Section

    def test_zgt(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        result = r.zgt('a', 1)
        assert len(result) == 4

    def test_zge(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        result = r.zge('a', 1)
        assert len(result) == 6

    def test_zlt(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        result = r.zlt('a', 3)
        assert len(result) == 4

    def test_zle(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        result = r.zle('a', 3)
        assert len(result) == 6

    def test_zgtcount(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zgtcount('a', 1) == 4

    def test_zgecount(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zgecount('a', 1) == 6

    def test_zltcount(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zltcount('a', 3) == 4

    def test_zlecount(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zlecount('a', 3) == 6

    def test_zuniquerank(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zuniquerank('a', 'x') == 0
        assert r.zuniquerank('a', 'xx') == 0
        assert r.zuniquerank('a', 'y') == 2
        assert r.zuniquerank('a', 'yy') == 2
        assert r.zuniquerank('a', 'z') == 4
        assert r.zuniquerank('a', 'zz') == 4

    def test_zuniquerevrank(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zuniquerevrank('a', 'x') == 4
        assert r.zuniquerevrank('a', 'xx') == 4
        assert r.zuniquerevrank('a', 'y') == 2
        assert r.zuniquerevrank('a', 'yy') == 2
        assert r.zuniquerevrank('a', 'z') == 0
        assert r.zuniquerevrank('a', 'zz') == 0

    def test_zmax(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zmax('a') == 'zz'
        assert r.zmax('a', withscores=True) == ('zz', 3.0)

    def test_zmin(self, r):
        r.zadd('a', x=1, y=2, z=3, xx=1, yy=2, zz=3)
        assert r.zmin('a') == 'x'
        assert r.zmin('a', withscores=True) == ('x', 1.0)

    def test_zrawscore(self, r):
        r.zaddwithstamps('a', x=1)
        assert r.zrawscore('a', 'x') == 1
        r.zincrbywithstamps('a', 'x', -1)
        assert r.zrawscore('a', 'x') == 0

    # Locks Section

    def test_acquire_lock(self, r):
        lockname = 'redis_extensions'
        assert r.acquire_lock(lockname)
        assert not r.acquire_lock(lockname, acquire_timeout=0.05)

    def test_release_lock(self, r):
        lockname = 'redis_extensions'
        identifier = r.acquire_lock(lockname)
        assert r.release_lock(lockname, identifier)
        assert not r.release_lock(lockname, identifier)

    # Verification Codes Section

    def test_vcode(self, r):
        phone = '18888888888'
        code, overtop = r.vcode(phone)
        assert len(code) == 6
        assert not overtop
        assert r.exists('redis:extensions:vcode:quota:' + phone)
        code, overtop = r.vcode(phone, quota=1)
        assert not code
        assert overtop

    def test_vcode_status(self, r):
        phone = '18888888888'
        code, overtop = r.vcode(phone)
        assert r.vcode_status(phone, code)
        code, overtop = r.vcode(phone, code_cast_func=int)
        assert r.vcode_status(phone, code)
        assert not r.vcode_status(phone, '4321')

    # Compatibility Section

    def test_compatibility(self, r):
        assert r.incrlimit('a') == 1
        assert r.incrlimit('a', 5) == 6
        assert r.incrlimit('a', 10, 10) == 10
        assert r.incrlimit('a', 10, 10, 12) == 12
